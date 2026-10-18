"""Focused v1.2 synthetic regressions. No network, index writes, or semantic judge."""

from copy import deepcopy
import json
from unittest.mock import Mock, patch

from google.genai._api_client import BaseApiClient
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import tracing_context
from streamlit.testing.v1 import AppTest

import rag
from gemini_protection import completed_payload
from planner import TOPICS, validate_plan
from usage_limits import Policy
from workflow import ALPHA_NOTICE, build_workflow, run_question, supported_parts, validate_citations


def response(payload, finish="STOP", error=None):
    return {"raw": AIMessage(content="", response_metadata={"finish_reason": finish}),
            "parsed": payload, "parsing_error": error}


def content_checks():
    # All prose below is synthetic. Tests establish mechanics, not travel facts.
    docs = [Document(id=f"fixture-{i}", page_content="Synthetic passage.",
                     metadata={"source": "synthetic.pdf", "page_start": i, "page_end": i + 1})
            for i in (1, 3)]
    part = lambda text, refs: {"text": text, "sources": refs}
    good = part("A supported alias and compound activity.", ["S1", "S2"])
    bad = part("Unverified claim.", ["S1", "S99"])
    state = {"question": "Fixture?", "retrieval_query": "Fixture?",
             "matches": [{"id": d.id, "metadata": d.metadata} for d in docs],
             "payload": {"answerable": True, "paragraphs": [bad, good]}}
    answer = validate_citations(state)["answer"]
    assert "Unverified" not in answer["text"] and "compound" in answer["text"]
    assert set(answer["cited_ids"]) == {"fixture-1", "fixture-3"}
    assert "PDF pages 1-2" in answer["text"] and "PDF pages 3-4" in answer["text"]
    assert supported_parts([part("Text [S1]", ["S1"])], {"S1": {}})[0][0]["text"] == "Text"
    prefs = {"departure": "Fixture", "destination": "Fixture", "days": 2, "transport": "Motorbike"}
    payload = {"status": "complete", "overview": [good],
               "days": [{"day": i, "title": "Alias / compound title", "activities": [good]} for i in (1, 2)],
               "guidance": [{"topic": t, "paragraphs": [good]} for t in TOPICS],
               "destination_options": [], "transport_alternatives": [], "limitations": []}
    state = {"preferences": prefs, "documents": docs, "payload": deepcopy(payload)}
    complete = validate_plan(state)["plan"]
    assert complete["status"] == "complete" and len(complete["days"]) == 2
    transfer = part("Optional jeep transfer after the bike approach; arrange locally. Parking and cost unknown.", ["S2"])
    state["payload"]["transport_alternatives"] = [transfer]
    assert len(validate_plan(state)["plan"]["days"]) == 2
    assert validate_plan(state)["plan"]["preferences"]["transport"] == "Motorbike"
    state["payload"]["destination_options"] = [
        {"title": "Unsupported option", "paragraphs": [bad]},
        {"title": "Alias and compound destination", "paragraphs": [good]},
        {"title": "Cross-section option", "paragraphs": [bad, good]}]
    state["payload"]["days"][0]["activities"] = [part("Ride the M-1 motorway.", ["S1"])]
    partial = validate_plan(state)["plan"]
    assert not partial["days"] and partial["status"] == "partial"
    assert len(partial["destination_options"]) == 2 and partial["transport_alternatives"]
    assert "Unverified" not in json.dumps(partial) and "Unsupported option" not in json.dumps(partial)
    assert not any("motorway" in o["text"] for o in partial["destination_options"])
    assert state["payload"]["days"], "Validation mutated the original response"
    state["payload"]["limitations"] = ["Synthetic unsupported claim: the whole region requires weeks."]
    cleaned = validate_plan(state)["plan"]
    assert not any("requires weeks" in line for line in cleaned["limitations"])
    assert cleaned["destination_options"] and cleaned["status"] == "partial"
    for finish, error in [("MAX_TOKENS", None), ("STOP", ValueError("synthetic parse error"))]:
        try:
            completed_payload(response(payload, finish, error))
        except ValueError:
            pass
        else:
            raise AssertionError("Incomplete/malformed output accepted")


def selection_checks():
    from retrieval import select_chat_evidence
    docs = [Document(id=str(i), page_content="General evidence." if i != 5 else "Distinct destination.")
            for i in range(10)]
    assert [d.id for d in select_chat_evidence("Distinct destination", docs)] == ["0", "1", "2", "3", "5"]
    assert select_chat_evidence("General evidence", docs) == docs[:5]
    assert select_chat_evidence("General evidence", docs[:3] + docs[:3]) == docs[:3]


def rewrite_checks():
    from verify_conversation import fixtures
    retriever, chat, queries, rewrites, generations = fixtures()
    rewriter = Mock()
    rewriter.with_structured_output.return_value = RunnableLambda(
        lambda _: response(None, error=ValueError("synthetic malformed rewrite")))
    graph = build_workflow(retriever, chat, rewriter, checkpointer=InMemorySaver())
    run_question(graph, "Tell me about Skardu.", thread_id="one")
    result = run_question(graph, "What about Skardu accommodation?", thread_id="one")
    assert result["retrieval_query"] == result["question"] and result["rewrite_fallback"]
    assert len(queries) == len(generations) == 2
    assert len(result["turns"]) == 2
    for failure in [RuntimeError("provider unavailable"), TimeoutError("completion uncertain")]:
        def fail(_):
            raise failure
        rewriter.with_structured_output.return_value = RunnableLambda(fail)
        counts = len(queries), len(generations)
        try:
            run_question(graph, "What about accommodation nearby?", thread_id="one")
        except type(failure):
            pass
        else:
            raise AssertionError("Provider failure did not stop the workflow")
        assert (len(queries), len(generations)) == counts


def notice_checks():
    from verify_conversation import fixtures
    from verify_planner import fixtures as planner_fixtures
    retriever, chat, _, _, _ = fixtures()
    graph, _, _, _ = planner_fixtures()
    with patch("usage_stats._command", return_value=None), patch("workflow.open_retriever", return_value=retriever), patch("workflow.chat_model", return_value=chat), \
            patch("planner_ui.planner_resources", return_value=graph), \
            patch("usage_limits.Policy.from_env", return_value=Policy(cooldown_seconds=0, workflows_per_minute=100)):
        app = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        app.chat_input[0].set_value("Tell me about Skardu.").run()
        assert not app.exception and sum(c.value == ALPHA_NOTICE for c in app.caption) == 1
        app.run()
        assert sum(c.value == ALPHA_NOTICE for c in app.caption) == 1
        app.radio(key="app_view").set_value("Plan a Trip").run()
        next(b for b in app.button if b.label == "Create my trip outline").click().run()
        assert not app.exception and app.session_state.trip_plan["days"]
        assert sum(c.value == ALPHA_NOTICE for c in app.caption) == 1
        # A restored v1.1 result has no new fields; it still renders the notice once.
        plan = app.session_state.trip_plan
        for key in ("destination_options", "transport_alternatives", "app_notes"):
            plan.pop(key, None)
        app.run()
        assert not app.exception and sum(c.value == ALPHA_NOTICE for c in app.caption) == 1
        app.radio(key="app_view").set_value("Chat").run()
        with patch("workflow.run_question", side_effect=ValueError("private raw JSON diagnostic")):
            app.chat_input[0].set_value("Tell me about Skardu.").run()
        assert not app.exception and app.error
        assert "private raw" not in app.error[0].value
        assert sum(c.value == ALPHA_NOTICE for c in app.caption) == 2  # One historical answer + one fallback.


if __name__ == "__main__":
    with tracing_context(enabled=False), \
            patch.object(BaseApiClient, "request", side_effect=AssertionError("No API calls authorized")), \
            patch.object(BaseApiClient, "async_request", side_effect=AssertionError("No API calls authorized")), \
            patch("langsmith.run_trees.RunTree.post", side_effect=AssertionError("No uploads authorized")):
        for check in (content_checks, selection_checks, rewrite_checks, notice_checks):
            check()
            print(f"{check.__name__}: pass")
    print("Synthetic mechanics only; zero Gemini calls. Real claim support needs separate review.")
