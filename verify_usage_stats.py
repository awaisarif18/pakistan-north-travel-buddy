"""Counter checks with mocked storage/actions. --live tests an isolated Upstash namespace."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
import json
import os
import subprocess
import sys
from threading import Lock
from unittest.mock import patch
from uuid import uuid4

from google.genai._api_client import BaseApiClient
from streamlit.testing.v1 import AppTest

import rag
import usage_stats as stats
from usage_limits import Policy, ProcessLimiter


class FakeStore:
    """Models the protocol under a lock; does NOT execute or validate Redis Lua."""

    def __init__(self):
        self.lock, self.rows, self.events, self.calls = Lock(), {}, {}, []

    def command(self, args):
        with self.lock:
            self.calls.append(args)
            if args[0] == "HMGET":
                return deepcopy(self.rows.get(args[1]))
            assert args[0] == "EVAL"
            key = args[3]
            if args[1] == stats.INIT:
                return deepcopy(self.rows.setdefault(key, ["0", "0", args[4]]))
            assert args[1] == stats.INCREMENT and args[2] == "2"
            if key not in self.rows:
                return None
            event, kind = args[4:6]
            if event not in self.events:
                index = stats.FIELDS.index(kind)
                self.rows[key][index] = str(int(self.rows[key][index]) + 1)
                self.events[event] = kind
            elif self.events[event] != kind:
                return None
            return deepcopy(self.rows[key])


def storage_checks():
    fake = FakeStore()
    with patch.object(stats, "_command", side_effect=fake.command):
        stats.read_stats.clear()
        assert stats.read_stats() is None  # A read cannot silently initialize totals.
        initial = stats.initialize()
        assert initial["questions"] == initial["trip_plans"] == 0
        ids = [str(uuid4()) for _ in range(12)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda rid: stats.record_completion("questions", rid), ids * 3))
        assert stats.initialize()["questions"] == 12  # Initialization cannot reset existing counts.
        assert stats.record_completion("trip_plans", ids[0]) is None
        assert stats.record_completion("trip_plans", str(uuid4()))["trip_plans"] == 1
        assert stats.record_completion("questions", "a question must never become an ID") is None
        assert stats.record_completion("questions", None) is None
        writes = [a for a in fake.calls if a[0] == "EVAL" and a[1] == stats.INCREMENT]
        assert len(writes) == 38 and all(a[-1] == "2592000" for a in writes)
        assert all(a[2] == "2" for a in writes), "One script, not separate check/increment requests"
        stats.read_stats.clear()
        assert stats.read_stats()["questions"] == 12
        count = len(fake.calls)
        stats.read_stats()
        assert len(fake.calls) == count
    # Transport tests cannot reach the network, even when local credentials exist.
    with patch.object(stats._HTTP, "open") as request, patch.dict(os.environ, {
            "UPSTASH_REDIS_REST_URL": "", "UPSTASH_REDIS_REST_TOKEN": ""}):
        assert stats._command(["HMGET"]) is None
        request.assert_not_called()
    with patch.object(stats._HTTP, "open", side_effect=TimeoutError("private diagnostic")) as request, \
            patch.dict(os.environ, {"UPSTASH_REDIS_REST_URL": "https://synthetic.upstash.io", "UPSTASH_REDIS_REST_TOKEN": "test-only"}):
        assert stats.record_completion("questions", str(uuid4())) is None
        assert request.call_count == 1 and request.call_args.kwargs["timeout"] == 3
        body = json.loads(request.call_args.args[0].data)
        assert body[0] == "EVAL" and "test-only" not in str(body)
    for values in [None, [None, None, None], ["-1", "0", "2026-10-18"], ["1", "0", "not-a-date"]]:
        assert stats._stats(values) is None
    stats.read_stats.clear()


def eligibility_checks():
    good = {"answer": {"text": "Supported.", "answerable": True, "cited_ids": ["fixture"]}, "payload": {}}
    assert stats.usable_chat(good)
    refusal = {"answer": {"text": rag.NOT_FOUND, "answerable": False, "cited_ids": []},
               "payload": {"answerable": False, "paragraphs": []}}
    assert stats.usable_chat(refusal)
    refusal["payload"]["answerable"] = True  # Bad citations filtered into a fallback.
    assert not stats.usable_chat(refusal)
    assert not stats.usable_chat({})
    assert not stats.usable_chat({"answer": {"text": "", "answerable": True, "cited_ids": ["fixture"]}})
    plan = {"status": "partial", "cited_ids": ["fixture"], "destination_options": [{"text": "Supported option."}]}
    assert stats.usable_plan(plan)
    plan["status"] = "complete"
    assert stats.usable_plan(plan)
    plan["status"] = "unsupported"
    assert not stats.usable_plan(plan)
    assert not stats.usable_plan({"status": "partial", "cited_ids": ["fixture"], "limitations": ["A warning only."]})


def ui_checks():
    from verify_conversation import fixtures
    from verify_planner import fixtures as planner_fixtures
    retriever, chat, queries, _, _ = fixtures()
    planner, planner_queries, generations, _ = planner_fixtures()
    store = FakeStore()
    policy = Policy(cooldown_seconds=0, chat_requests=20, workflows_per_minute=100,
                    generation_calls_per_minute=100, embedding_calls_per_minute=100)
    limiter = ProcessLimiter(policy)
    with patch.object(stats, "_command", side_effect=store.command), \
            patch("workflow.open_retriever", return_value=retriever), patch("workflow.chat_model", return_value=chat), \
            patch("planner_ui.planner_resources", return_value=planner), \
            patch("usage_limits.ProcessLimiter", return_value=limiter):
        stats.read_stats.clear()
        stats.initialize()
        app = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert not app.exception and not store.events
        app.chat_input[0].set_value("Tell me about Skardu.").run()
        assert not app.exception and len(store.events) == 1
        calls = len(queries)
        app.run()
        assert len(store.events) == 1 and len(queries) == calls
        app.chat_input[0].set_value("What is the live weather in Skardu?").run()
        assert len(store.events) == 2  # A usable unsupported-question refusal counts.
        app.radio(key="app_view").set_value("Plan a Trip").run()
        assert len(store.events) == 2
        next(b for b in app.button if b.label == "Create my trip outline").click().run()
        assert not app.exception and len(store.events) == 3 and len(generations) == 1
        app.run()
        assert len(store.events) == 3 and len(generations) == 1
        next(b for b in app.button if b.label == "Create my trip outline").click().run()
        assert not app.exception and len(store.events) == 3  # Blocked planner submission.
        app.radio(key="app_view").set_value("Chat").run()
        app.button(key="clear_chat").click().run()
        assert len(store.events) == 3
        # An example click counts its completed answer, never the click separately.
        next(b for b in app.button if b.label == "Rakaposhi trekking season").click().run()
        assert not app.exception and len(store.events) == 4
        with patch("workflow.run_question", side_effect=ValueError("Synthetic technical failure")):
            app.chat_input[0].set_value("Tell me about Skardu.").run()
        assert not app.exception and len(store.events) == 4
        with patch.object(stats, "record_completion", side_effect=TimeoutError("Synthetic store failure")) as record:
            app.chat_input[0].set_value("Tell me about Skardu.").run()
            assert not app.exception and record.call_count == 1
            assert any(stats.UNAVAILABLE in el.value for el in app.get("html"))
            app.run()
            assert record.call_count == 1, "A rerun retried a failed write"
        assert len(store.events) == 4
        other = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert not other.exception
        assert "pending_usage_counts" not in other.session_state
        assert any("Questions answered" in el.value and ">3<" in el.value for el in other.get("html"))
        other.chat_input[0].set_value("Tell me about Skardu.").run()
        assert len(store.events) == 5 and other.session_state.usage["subject_id"] != app.session_state.usage["subject_id"]
    stats.read_stats.clear()


def live_checks():
    """At most 40 REST requests. Only a disposable namespace receives synthetic writes."""
    namespace = "north-tours:public-usage:check:" + uuid4().hex
    request_ids = [str(uuid4()) for _ in range(12)]
    commands, lock = [], Lock()
    original = stats._command

    def limited(args):
        with lock:
            assert len(commands) < 40, "Store request budget reached"
            assert namespace in str(args), "Production namespace is forbidden in live tests"
            commands.append(args)
        return original(args)

    with patch.object(stats, "_command", side_effect=limited):
        try:
            assert stats.initialize(namespace=namespace) is not None, "Store setup unavailable"
            with ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(lambda rid: stats.record_completion("questions", rid, namespace=namespace), request_ids * 2))
            assert all(r is not None for r in results)
            stored = stats._stats(stats._command(["HMGET", *stats.keys(namespace), *stats.FIELDS]))
            assert stored["questions"] == 12 and stored["trip_plans"] == 0
            assert stats.initialize(namespace=namespace) == stored
            assert stats.record_completion("trip_plans", str(uuid4()), namespace=namespace)["trip_plans"] == 1
            ttl = stats._command(["TTL", stats.keys(namespace, request_ids[0])[1]])
            assert 0 < ttl <= stats.RETENTION_SECONDS
            assert stats._command(["TTL", stats.keys(namespace)[0]]) == -1
            # Reserve one request for a separate process with a fresh HTTP client.
            commands.append(["FRESH_PROCESS_READ", namespace])
            code = ("import json,sys; import usage_stats as s; "
                    "print(json.dumps(s._stats(s._command(['HMGET', *s.keys(sys.argv[1]), *s.FIELDS]))))")
            child = subprocess.run([sys.executable, "-c", code, namespace], cwd=rag.ROOT,
                                   capture_output=True, text=True, timeout=15, check=True)
            persisted = json.loads(child.stdout)
            assert persisted["questions"] == 12 and persisted["trip_plans"] == 1
            print("Actual Upstash: atomic/deduplicated writes, both totals, TTLs and persistence across client-process restart passed.")
        finally:
            test_keys = [args[4] for args in commands if args[:2] == ["EVAL", stats.INCREMENT]]
            deleted = stats._command(["DEL", *stats.keys(namespace), *dict.fromkeys(test_keys)])
            assert isinstance(deleted, int), "Test cleanup was not acknowledged"
    print(f"Actual store requests: {len(commands)}; production writes: 0; Gemini calls: 0.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Use configured credentials, only an isolated test namespace.")
    args = parser.parse_args()
    if args.live:
        from dotenv import load_dotenv
        load_dotenv(rag.ROOT / ".env")
        live_checks()
    else:
        with ExitStack() as stack:
            stack.enter_context(patch.object(BaseApiClient, "request", side_effect=AssertionError("No Gemini calls authorized")))
            stack.enter_context(patch("langsmith.run_trees.RunTree.post", side_effect=AssertionError("No uploads authorized")))
            for check in (storage_checks, eligibility_checks, ui_checks):
                check()
                print(check.__name__ + ": pass")
        print("Mocked store/protocol and workflow checks only. Actual Redis atomicity/persistence unverified until --live.")
