"""Seven controlled memory scenarios, without Gemini or the retrieval benchmark."""

import argparse
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

from langchain_core.messages import AIMessage
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import get_current_run_tree, traceable, tracing_context
from langsmith.run_helpers import get_tracing_context

import rag
from eval_metrics import citation_validity
from workflow import build_workflow, run_question, validate_citations

OUTPUT = rag.DATA_DIR / "conversation-checks"


def fixtures():
    queries, rewrites, generations = [], [], []
    destinations = {"Rakaposhi Base Camp": (20, "fixture-rakaposhi"), "Skardu": (37, "fixture-skardu")}

    def retrieve(question):
        queries.append(question)
        topic = next((name for name in destinations if name in question), None)
        if not topic:
            return []
        page, source_id = destinations[topic]
        return [Document(id=source_id, page_content=f"Controlled test evidence about {topic}.",
                         metadata={"source": "synthetic.pdf", "page_start": page, "page_end": page})]

    def structured(schema, **options):
        def respond(prompt):
            context = json.loads(prompt.messages[-1].content)
            if "standalone_query" in schema["properties"]:
                rewrites.append(context)
                recent = context["recent_exchanges"]
                assert 1 <= len(recent) <= 4
                topic = next(name for name in destinations if name in recent[-1]["resolved_question"])
                return {"standalone_query": f"{context['question']} Destination: {topic}."}
            assert set(context) == {"question", "excerpts"}, "Conversation facts reached answer generation"
            generations.append(context)
            if "live weather" in context["question"]:
                return {"answerable": False, "paragraphs": []}
            return {"answerable": True, "paragraphs": [
                {"text": context["excerpts"][0]["text"], "sources": ["S1"]}]}
        def envelope(prompt):
            payload = respond(prompt)
            return {"raw": AIMessage(content="", response_metadata={"finish_reason": "STOP"}),
                    "parsed": payload, "parsing_error": None} if options.get("include_raw") else payload
        return RunnableLambda(envelope)

    chat = Mock()
    chat.with_structured_output.side_effect = structured
    return RunnableLambda(retrieve, name="ControlledRetriever"), chat, queries, rewrites, generations


@traceable(name="conversation-memory-controlled-seven-scenarios")
def controlled_checks(trace=False):
    retriever, chat, queries, rewrites, generations = fixtures()
    graph = build_workflow(retriever, chat, chat, checkpointer=InMemorySaver())
    thread = str(uuid4())
    records, results = [], []
    root = get_current_run_tree()

    def ask(question, *, target=graph, thread_id=thread, topic=None, unchanged=False):
        before = len(target.get_state({"configurable": {"thread_id": thread_id}}).values.get("turns", []))
        state = run_question(target, question, thread_id=thread_id, trace=trace)
        assert state["question"] == question and state["turns"][-1]["question"] == question
        assert len(state["turns"]) == before + 1
        assert citation_validity({"answer": state["answer"], "matches": state["matches"]})["score"] == 1
        if topic:
            assert topic in state["retrieval_query"]
        if unchanged:
            assert state["retrieval_query"] == question
        records.append({"question": question, "retrieval_query": state["retrieval_query"],
                        "answer": state["answer"], "thread_id": thread_id})
        return state

    ask("Tell me about Rakaposhi Base Camp.", unchanged=True)
    ask("What's the best season?", topic="Rakaposhi Base Camp")
    results.append({"scenario": "Follow-up destination resolution", "status": "pass"})
    ask("What about accommodation nearby?", topic="Rakaposhi Base Camp")
    results.append({"scenario": "Accommodation follow-up", "status": "pass"})
    ask("How much would that cost?", topic="Rakaposhi Base Camp")
    results.append({"scenario": "Cost follow-up", "status": "pass"})
    ask("Tell me about Skardu.", unchanged=True)
    ask("What's the best season?", topic="Skardu")
    assert len(rewrites[-1]["recent_exchanges"]) == 4
    results.append({"scenario": "Switching destinations", "status": "pass"})

    fresh = build_workflow(retriever, chat, chat, checkpointer=InMemorySaver())
    fresh_id = str(uuid4())
    assert fresh.checkpointer is not graph.checkpointer
    assert not fresh.get_state({"configurable": {"thread_id": fresh_id}}).values
    reset = ask("What's the best season?", target=fresh, thread_id=fresh_id, unchanged=True)
    assert reset["answer"]["text"] == rag.NOT_FOUND and len(reset["turns"]) == 1
    results.append({"scenario": "Clear conversation", "status": "pass"})

    count = len(rewrites)
    ask("  Where should I refuel before traveling to Khunjerab Pass?  ", unchanged=True)
    assert len(rewrites) == count
    results.append({"scenario": "Unrelated standalone question", "status": "pass"})

    # Distinct threads on one graph, and distinct session-owned savers, both isolate context.
    other_id = str(uuid4())
    ask("Tell me about Rakaposhi Base Camp.", thread_id=other_id, unchanged=True)
    ask("What's the best season?", thread_id=other_id, topic="Rakaposhi Base Camp")
    assert len(graph.get_state({"configurable": {"thread_id": other_id}}).values["turns"]) == 2
    assert len(graph.get_state({"configurable": {"thread_id": thread}}).values["turns"]) == 7
    assert len(fresh.get_state({"configurable": {"thread_id": fresh_id}}).values["turns"]) == 1
    results.append({"scenario": "Two-session separation", "status": "pass"})
    refusal = ask("What is the live weather in Skardu?", unchanged=True)
    assert refusal["answer"]["text"] == rag.NOT_FOUND

    for paragraphs in [[], [{"text": "Unsupported", "sources": []}],
                       [{"text": "Unsupported", "sources": ["S99"]}]]:
        result = validate_citations({"question": "Fixture?", "retrieval_query": "Fixture?",
                                    "matches": [{"id": "fixture", "metadata": {}}],
                                    "payload": {"answerable": True, "paragraphs": paragraphs}})
        assert not result["answer"]["answerable"] and not result["answer"]["cited_ids"]
    # Ambient tracing must not override the frontend's explicit opt-out.
    with patch.dict(os.environ, {"LANGSMITH_TRACING": "true"}):
        def private_retrieve(_):
            assert get_tracing_context()["enabled"] is False
            return [Document(id="private-fixture", page_content="Private fixture.",
                             metadata={"page_start": 1, "page_end": 1})]
        def private_generate(_):
            assert get_tracing_context()["enabled"] is False
            return {"raw": AIMessage(content="", response_metadata={"finish_reason": "STOP"}),
                    "parsed": {"answerable": True, "paragraphs": [{"text": "Private fixture.", "sources": ["S1"]}]},
                    "parsing_error": None}
        private_chat = Mock()
        private_chat.with_structured_output.return_value = RunnableLambda(private_generate)
        private = build_workflow(RunnableLambda(private_retrieve), private_chat, private_chat, checkpointer=InMemorySaver())
        with patch("langsmith.run_trees.RunTree.post") as upload:
            run_question(private, "Privacy fixture", thread_id=str(uuid4()), trace=False)
            upload.assert_not_called()
    return {"mode": "controlled fixtures, no Gemini or Chroma", "results": results, "turns": records,
            "rewrite_calls": len(rewrites), "generation_calls": len(generations),
            "max_rewrite_exchanges": max(len(x["recent_exchanges"]) for x in rewrites),
            "citation_validation": "pass", "unsupported_refusal": "pass", "production_trace_opt_out": "pass",
            "trace_id": str(root.id) if root else None, "trace_url": root.get_url() if root else None}


def check_streamlit():
    from streamlit.testing.v1 import AppTest
    from usage_limits import Policy

    retriever, chat, queries, _, _ = fixtures()
    policy = Policy(cooldown_seconds=0, workflows_per_minute=100, generation_calls_per_minute=100,
                    embedding_calls_per_minute=100)  # Test-only capacity; not provider quotas.
    with patch("usage_stats._command", return_value=None), patch("workflow.open_retriever", return_value=retriever), patch("workflow.chat_model", return_value=chat), \
            patch("usage_limits.Policy.from_env", return_value=policy):
        app = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert not app.exception
        initial_id, graph = app.session_state.conversation
        app.chat_input[0].set_value("Tell me about Rakaposhi Base Camp.").run()
        assert not app.exception
        app.chat_input[0].set_value("What's the best season?").run()
        assert not app.exception
        turn_count = len(graph.get_state({"configurable": {"thread_id": initial_id}}).values["turns"])
        calls = len(queries)
        app.run()
        assert not app.exception and len(queries) == calls and turn_count == 2
        assert len(graph.get_state({"configurable": {"thread_id": initial_id}}).values["turns"]) == 2
        assert "What's the best season?" in [m.value for m in app.markdown]
        app.button(key="clear_chat").click().run()
        new_id, new_graph = app.session_state.conversation
        assert not app.exception and new_id != initial_id and new_graph.checkpointer is not graph.checkpointer
        assert not new_graph.get_state({"configurable": {"thread_id": new_id}}).values
        other = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        other_id, other_graph = other.session_state.conversation
        assert not other.exception and other_id not in {initial_id, new_id}
        assert other_graph.checkpointer is not new_graph.checkpointer
        assert not other_graph.get_state({"configurable": {"thread_id": other_id}}).values
    return "pass: initial view, original questions, follow-up, no rerun duplicate/call, reset, separate sessions"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", action="store_true", help="Upload synthetic development traces only.")
    args = parser.parse_args()
    if args.trace and not (os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT")):
        parser.error("Configure private LangSmith development credentials before --trace.")
    with tracing_context(enabled=args.trace, project_name=os.getenv("LANGSMITH_PROJECT")):
        result = controlled_checks(trace=args.trace)
    with tracing_context(enabled=False):
        result["streamlit"] = check_streamlit()
    if args.trace:
        from langsmith.run_trees import get_cached_client
        client = get_cached_client()
        client.flush()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "controlled.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "turns"}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
