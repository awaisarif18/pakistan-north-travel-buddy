"""Portable terminal-only release checks: no browser, AppTest, Gemini, index writes or tracing."""

import json
import os
from pathlib import Path
import socket
import unittest
from unittest.mock import Mock, patch

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from google.genai._api_client import BaseApiClient
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import tracing_context

import recommendations as rec
from usage_limits import Policy, ProcessLimiter, api_call, new_usage
from workflow import build_workflow, run_question

ROOT = Path(__file__).resolve().parent


def fixtures(replies):
    replies = iter(replies)
    documents = [Document(id="fixture", page_content="Synthetic source evidence.",
                         metadata={"source": "synthetic.pdf", "page_start": 1, "page_end": 2})]
    contexts = []

    def retrieve(query):
        with api_call("embedding"):
            return documents

    def respond(prompt):
        contexts.append(json.loads(prompt.messages[-1].content))
        reply = next(replies)
        if isinstance(reply, Exception):
            raise reply
        return {"raw": AIMessage(content="", response_metadata={"finish_reason": "STOP"}),
                "parsed": reply, "parsing_error": None}

    model = Mock()
    model.with_structured_output.return_value = RunnableLambda(respond)
    graph = build_workflow(RunnableLambda(retrieve), model, model, checkpointer=InMemorySaver(),
                           recommendation_catalog=[{"id": "fixture", "name": "Fixture", "facts": [], "unknowns": []}])
    limiter = ProcessLimiter(Policy(cooldown_seconds=0))
    return graph, limiter, contexts


def decision(mode="answer", text="Synthetic factual answer."):
    return {"answerable": bool(text), "paragraphs": [{"text": text, "sources": ["S1"]}] if text else [],
            "decision": mode, "conversation_scope": "new_topic", "preferences": {},
            "candidate_ids": ["fixture"], "queries": []}


def ask(graph, limiter):
    with limiter.workflow(new_usage(), "chat", "fixture", "Synthetic question", api_budget={"generation": 1, "embedding": 1}):
        return run_question(graph, "Synthetic question", thread_id="fixture", trace=False)


class ReleaseChecks(unittest.TestCase):
    def test_direct_factual_answer_does_not_expand_for_candidate_hints(self):
        graph, limiter, _ = fixtures([decision()])
        result = ask(graph, limiter)
        self.assertIn("PDF pages 1-2", result["answer"]["text"])
        self.assertEqual(limiter.daily_calls, {"generation": 1, "embedding": 1})

    def test_information_request_generates_only_final_personalized_answer(self):
        graph, limiter, contexts = fixtures([decision("recommend", "Discarded provisional draft."),
                                           {"paragraphs": [{"text": "Synthetic final answer.", "sources": ["S1"]}]}])
        result = ask(graph, limiter)
        self.assertNotIn("provisional", result["answer"]["text"])
        self.assertNotIn("provisional", json.dumps(contexts[-1]))
        self.assertEqual(limiter.daily_calls["generation"], 2)
        self.assertIn("source_annotations", contexts[-1])

    def test_empty_answer_recovers_once(self):
        graph, limiter, _ = fixtures([decision(text=""), {"paragraphs": [{"text": "Synthetic recovered answer.", "sources": ["S1"]}]}])
        self.assertIn("recovered", ask(graph, limiter)["answer"]["text"])
        self.assertEqual(limiter.daily_calls["generation"], 2)

    def test_provider_failure_preserves_sources_without_retry_or_draft(self):
        graph, limiter, contexts = fixtures([decision("recommend", "Discarded provisional draft."), TimeoutError()])
        result = ask(graph, limiter)
        self.assertTrue(result["answer"]["technical_failure"])
        self.assertEqual(result["answer"]["cited_ids"], [])
        self.assertTrue(result["matches"])
        self.assertEqual(len(contexts), 2)

    def test_beta_configuration_and_baseline(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('os.getenv("ENABLE_RECOMMENDATIONS", "true")', source)
        self.assertIn("Destination recommendations are BETA", source)
        baseline = json.loads((ROOT / "evals/v1_3_development_baseline.json").read_text(encoding="utf-8"))
        self.assertEqual(baseline["summary"]["overall_pass"], 3)
        self.assertEqual(baseline["summary"]["joint_usefulness_and_full_alignment"], 4)
        self.assertEqual(len(baseline["cases"]), 8)
        self.assertEqual(baseline["prompt_snapshot"]["final_recommendation_system"], rec.FINAL)


def main():
    original = socket.socket.connect

    def localhost_only(sock, address):
        if not isinstance(address, tuple) or address[0] not in {"127.0.0.1", "::1"}:
            raise AssertionError("External network forbidden in offline release checks")
        return original(sock, address)

    with patch("socket.socket.connect", new=localhost_only), tracing_context(enabled=False), \
            patch.object(BaseApiClient, "request", side_effect=AssertionError("No Gemini calls")) as sdk, \
            patch.object(BaseApiClient, "async_request", side_effect=AssertionError("No async calls")), \
            patch("langsmith.run_trees.RunTree.post", side_effect=AssertionError("No trace uploads")) as trace:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseChecks))
        assert result.wasSuccessful()
        import verify_conversation as conversation
        import verify_usage as usage
        import verify_planner as planner
        import verify_simplification as rendering
        print(conversation.controlled_checks(trace=False)["results"])
        for check in [usage.session_checks, usage.capacity_checks, usage.concurrency_checks,
                      usage.boundary_checks, usage.quota_checks, planner.graph_checks,
                      planner.guidance_checks, planner.quota_checks, rendering.content_checks,
                      rendering.selection_checks, rendering.rewrite_checks]:
            check()
            print(check.__module__ + "." + check.__name__ + ": pass")
        assert sdk.call_count == trace.call_count == 0
        print("No UI tests. Real Gemini/embedding calls: 0. Trace uploads: 0.")


if __name__ == "__main__":
    main()
