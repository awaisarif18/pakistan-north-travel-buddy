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
    def test_startup_refreshes_legacy_imports_without_resetting_normal_reruns(self):
        import subprocess
        import sys
        # Synthetic old API: remove only the two members introduced in v1.3.
        # A subprocess prevents disturbing the quota ContextVar in the other tests.
        code = '''import ast, sys, types
from pathlib import Path
from unittest.mock import Mock
root=Path.cwd()
tree=ast.parse((root/'usage_limits.py').read_text(encoding='utf-8'))
tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef) and n.name=='reserve_additional_calls')]
limiter=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ProcessLimiter')
limiter.body=[n for n in limiter.body if not (isinstance(n,ast.FunctionDef) and n.name=='extend')]
old=types.ModuleType('usage_limits');old.__file__=str(root/'usage_limits.py');sys.modules['usage_limits']=old
exec(compile(tree,old.__file__,'exec'),old.__dict__)
try:
 import recommendations
except ImportError as e:
 assert 'reserve_additional_calls' in str(e)
else:raise AssertionError('Legacy failure not reproduced')
for name in ('workflow','planner'):
 sys.modules[name]=types.ModuleType(name)
from runtime_bootstrap import refresh_legacy_runtime
clear=Mock()
assert refresh_legacy_runtime(clear) is True
clear.assert_called_once()
import recommendations,usage_limits,gemini_protection,workflow,planner
assert recommendations.reserve_additional_calls is usage_limits.reserve_additional_calls
assert gemini_protection.api_call is usage_limits.api_call
assert callable(workflow.build_workflow) and callable(planner.build_planner)
context=usage_limits._CURRENT_LIMITER
assert refresh_legacy_runtime(clear) is False and usage_limits._CURRENT_LIMITER is context
clear.assert_called_once()
print('Legacy import reproduced, refreshed, and fresh rerun left unchanged.')
'''
        done = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_legacy_graph_reset_keeps_session_usage_and_planner_result(self):
        from types import SimpleNamespace
        from runtime_bootstrap import discard_legacy_conversation
        usage = new_usage()
        state = {"conversation": ("old", SimpleNamespace(nodes={"validate_citations": None})),
                 "pending_submission": {"text": "old pending"}, "usage": usage, "trip_plan": "retained"}
        discard_legacy_conversation(state)
        self.assertNotIn("conversation", state)
        self.assertNotIn("pending_submission", state)
        self.assertIs(state["usage"], usage)
        self.assertEqual(state["trip_plan"], "retained")
        state["conversation"] = ("current", SimpleNamespace(nodes={"recommend_destinations": None}))
        discard_legacy_conversation(state)
        self.assertIn("conversation", state)

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
        self.assertLess(source.index("refresh_legacy_runtime(st.cache_resource.clear)"), source.index("from recommendations import"))
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
