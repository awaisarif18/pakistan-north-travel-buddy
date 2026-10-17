"""Focused synthetic planner and feedback checks, with no Gemini requests."""

from copy import deepcopy
import json
import os
from unittest.mock import Mock, patch

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langsmith import tracing_context
from streamlit.testing.v1 import AppTest

import rag
from planner import API_BUDGET, TOPICS, build_planner, run_trip, validate_plan, validate_preferences
from usage_limits import BUSY, QUOTA, Policy, ProcessLimiter, UsageLimitError, new_usage

CASES = json.loads((rag.ROOT / "evals/trip_cases.json").read_text(encoding="utf-8"))


def fixtures():
    queries, calls = [], []
    documents = [Document(id="fixture-hunza", page_content="Controlled Hunza evidence.",
                          metadata={"source": "synthetic.pdf", "page_start": 20, "page_end": 22})]

    def retrieve(query):
        queries.append(query)
        return documents

    def structured(schema, **_):
        def respond(prompt):
            calls.append(1)
            p = json.loads(prompt.messages[-1].content)["preferences"]
            unsupported = p["destination"] == "Moon"
            short = p["days"] == 1
            part = {"text": "Controlled Hunza evidence.", "sources": ["S1"]}
            return {"status": "unsupported" if unsupported else "partial" if short else "complete",
                    "overview": [] if unsupported else [part],
                    "days": [] if short or unsupported else [
                        {"day": i, "title": "Controlled activity", "activities": [part]} for i in range(1, p["days"] + 1)],
                    "guidance": [] if unsupported else [{"topic": topic, "paragraphs": [part]} for topic in TOPICS],
                    "limitations": ["This trip cannot be established from the evidence."] if short or unsupported else []}
        return RunnableLambda(respond)

    model = Mock()
    model.with_structured_output.side_effect = structured
    return build_planner(RunnableLambda(retrieve), model), queries, calls, documents


def graph_checks():
    graph, queries, calls, documents = fixtures()
    plans = [run_trip(graph, case["preferences"])["plan"] for case in CASES]
    assert len(queries) == 9 and len(calls) == 3
    assert all("PDF pages 20-22" in plan["overview"] for plan in plans)
    assert plans[0]["preferences"]["transport"] == "Motorbike" and len(plans[0]["days"]) == 5
    assert plans[1]["preferences"]["destination"] == "Skardu" and len(plans[1]["days"]) == 3
    assert "Confirm access locally" in plans[1]["guidance"]["Transport"]
    assert "Controlled Hunza evidence" not in plans[1]["guidance"]["Transport"]
    assert plans[2]["status"] == "partial" and not plans[2]["days"]
    assert all(set(plan["cited_ids"]) <= {"fixture-hunza"} for plan in plans)
    other = {**CASES[0]["preferences"], "destination": "Moon"}
    assert run_trip(graph, other)["plan"]["status"] == "unsupported"
    for preferences in [{**other, "days": 0}, {**other, "days": 11}, {**other, "departure": " "},
                        {**other, "transport": "Rocket"}, {**other, "interests": []}]:
        try:
            validate_preferences(preferences)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid preferences accepted")
    state = graph.invoke({"preferences": CASES[0]["preferences"]})
    for invalid in ["bad_source", "bad_day", "empty_activity"]:
        broken = deepcopy(state)
        if invalid == "bad_source":
            broken["payload"]["overview"][0]["sources"] = ["S99"]
        elif invalid == "bad_day":
            broken["payload"]["days"][0]["day"] = 8
        else:
            broken["payload"]["days"][0]["activities"] = []
        try:
            validate_plan(broken)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid citation/day accepted")
    empty = build_planner(RunnableLambda(lambda _: []), Mock())
    assert run_trip(empty, CASES[0]["preferences"])["plan"]["status"] == "unsupported"


def quota_checks():
    graph, queries, calls, _ = fixtures()
    clock = [10000.0]
    limiter = ProcessLimiter(Policy(), clock=lambda: clock[0])
    usage = new_usage()
    with limiter.workflow(usage, "trip_plan", "one", "Hunza", api_budget=API_BUDGET):
        run_trip(graph, CASES[0]["preferences"])
    assert limiter.daily_calls["generation"] == 1 and len(calls) == 1
    clock[0] += 12
    try:
        with limiter.workflow(usage, "trip_plan", "two", "Hunza", api_budget=API_BUDGET):
            run_trip(graph, CASES[0]["preferences"])
    except UsageLimitError as error:
        assert str(error) == QUOTA
    else:
        raise AssertionError("Planner quota was bypassed")
    busy = ProcessLimiter(Policy(generation_calls_per_minute=1))
    with busy.api_call("generation"):
        pass
    try:
        with busy.workflow(new_usage(), "trip_plan", "busy", "Hunza", api_budget=API_BUDGET):
            run_trip(graph, CASES[0]["preferences"])
    except UsageLimitError as error:
        assert str(error) == BUSY
    else:
        raise AssertionError("Global generation guard was bypassed")
    assert len(calls) == 1 and len(queries) == 3


def ui_checks():
    from verify_conversation import fixtures as chat_fixtures
    graph, queries, calls, _ = fixtures()
    retriever, chat, _, _, _ = chat_fixtures()
    clock = [10000.0]
    limiter = ProcessLimiter(Policy(), clock=lambda: clock[0])
    with patch("workflow.open_retriever", return_value=retriever), patch("workflow.chat_model", return_value=chat), \
            patch("usage_limits.ProcessLimiter", return_value=limiter), patch("planner_ui.planner_resources", return_value=graph):
        app = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert not app.exception
        links = {link.label: link.url for link in app.link_button}
        target = "https://forms.gle/5McdABdSnigwwdNz5"
        assert links["Send Feedback"] == links["Help Test Future Releases"] == target
        assert "?" not in links["Send Feedback"] and not calls
        app.radio(key="app_view").set_value("Plan a Trip").run()
        app.text_input(key="trip_departure").set_value(" ")
        next(b for b in app.button if b.label == "Create my trip outline").click().run()
        assert not calls and limiter.remaining(app.session_state.usage, "trip_plan") == 1
        app.text_input(key="trip_departure").set_value("Gilgit")
        with patch.dict(os.environ, {"LANGSMITH_TRACING": "true"}), patch("langsmith.run_trees.RunTree.post") as upload:
            next(b for b in app.button if b.label == "Create my trip outline").click().run()
            upload.assert_not_called()
        assert not app.exception and len(calls) == 1 and len(queries) == 3
        assert app.session_state.trip_plan["preferences"]["destination"] == "Hunza"
        app.run()
        assert not app.exception and len(calls) == 1
        clock[0] += 12
        next(b for b in app.button if b.label == "Create my trip outline").click().run()
        assert not app.exception and len(calls) == 1 and any(item.value == QUOTA for item in app.info)
        assert len(app.link_button) == 2
        other = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert "trip_plan" not in other.session_state
        assert other.session_state.usage["subject_id"] != app.session_state.usage["subject_id"]
        app.button(key="clear_chat").click().run()
        assert limiter.remaining(app.session_state.usage, "trip_plan") == 0
        # Exhaust global generation headroom in a fresh session; both links remain available.
        limiter.daily_calls["generation"] = limiter.policy.generation_calls_per_day
        other.radio(key="app_view").set_value("Plan a Trip").run()
        next(b for b in other.button if b.label == "Create my trip outline").click().run()
        assert not other.exception and len(calls) == 1 and len(other.link_button) == 2


def main():
    results = {}
    with tracing_context(enabled=False):
        for check in [graph_checks, quota_checks, ui_checks]:
            check()
            results[check.__name__] = "pass"
    folder = rag.DATA_DIR / "planner-checks"
    folder.mkdir(exist_ok=True)
    (folder / "mock_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    print("Zero real Gemini calls. Synthetic output tests do not measure actual itinerary quality.")


if __name__ == "__main__":
    main()
