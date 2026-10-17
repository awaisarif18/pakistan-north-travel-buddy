"""Focused usage-policy checks. All workflows and Gemini operations are fake."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from contextvars import copy_context
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier, Event, Lock
from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain_core.runnables import RunnableLambda
from langsmith import tracing_context

import rag
from gemini_protection import invoke_chat
from verify_quota_windows import quota_checks
from usage_limits import (BUSY, COOLDOWN, PROVIDER_BUSY, QUOTA, UNCONFIGURED, Policy,
                          ProcessLimiter, UsageLimitError, api_call, new_usage)


def setup(**overrides):
    clock = [10000.0]
    policy = Policy(**{**dict(workflows_per_minute=100, generation_calls_per_minute=100,
                              embedding_calls_per_minute=100), **overrides})
    return ProcessLimiter(policy, clock=lambda: clock[0]), clock, new_usage()


@contextmanager
def denied(message):
    try:
        yield
    except UsageLimitError as error:
        assert str(error) == message
    else:
        raise AssertionError("Expected admission to be denied")


def session_checks():
    limiter, clock, usage = setup()
    fake = Mock()
    for i in range(3):
        with limiter.workflow(usage, "chat", str(i), "Question"):
            fake()
        clock[0] += 12
    assert fake.call_count == 3 and limiter.remaining(usage) == 0
    with denied(QUOTA), limiter.workflow(usage, "chat", "fourth", "Question"):
        fake()
    assert fake.call_count == 3
    clock[0] += 3600
    assert limiter.remaining(usage) == 3
    with limiter.workflow(usage, "chat", "new-window", "Question"):
        pass
    with denied(COOLDOWN), limiter.workflow(usage, "chat", "rapid", "Question"):
        fake()
    second = new_usage()
    assert second["subject_id"] != usage["subject_id"]
    with limiter.workflow(second, "chat", "separate", "Question"):
        pass
    assert limiter.remaining(second) == 2 and limiter.remaining(usage) == 2
    clock[0] += 12
    with denied("This question has already been submitted."), limiter.workflow(usage, "chat", "new-window", "Question"):
        fake()
    assert limiter.remaining(usage) == 2
    with denied("Please enter a question of 1 to 700 characters."), limiter.workflow(usage, "chat", "long", "x" * 701):
        fake()
    planner = new_usage()
    for i in range(1):
        with limiter.workflow(planner, "trip_plan", str(i), "Fake plan", api_budget={"generation": 0, "embedding": 0}):
            pass
        clock[0] += 12
    with denied(QUOTA), limiter.workflow(planner, "trip_plan", "second", "Fake plan", api_budget={"generation": 0, "embedding": 0}):
        fake()
    assert limiter.remaining(planner, "trip_plan") == 0 and limiter.remaining(planner, "chat") == 3
    # Configurability also preserves the original eight-request policy when chosen.
    legacy, legacy_clock, legacy_usage = setup(chat_requests=8)
    for i in range(8):
        with legacy.workflow(legacy_usage, "chat", str(i), "Question"):
            pass
        legacy_clock[0] += 12
    with denied(QUOTA), legacy.workflow(legacy_usage, "chat", "ninth", "Question"):
        fake()


def capacity_checks():
    limiter, clock, usage = setup(workflows_per_minute=1)
    with limiter.workflow(usage, "chat", "first", "Question"):
        pass
    blocked = new_usage()
    with denied(BUSY), limiter.workflow(blocked, "chat", "second", "Question"):
        raise AssertionError("Blocked workflow started")
    assert limiter.remaining(blocked) == 3
    clock[0] += 60
    with limiter.workflow(blocked, "chat", "second", "Question"):
        pass
    no_capacity, _, usage = setup(generation_calls_per_minute=1)
    with denied(BUSY), no_capacity.workflow(usage, "chat", "insufficient-api-budget", "Question", api_budget={"generation": 2}):
        raise AssertionError("Known API-capacity shortage reached a workflow")
    assert no_capacity.active == 0 and no_capacity.remaining(usage) == 3
    unknown = ProcessLimiter(Policy(workflows_per_minute=None))
    with denied(UNCONFIGURED), unknown.workflow(new_usage(), "chat", "unset", "Question"):
        raise AssertionError("Unconfigured public admission was allowed")
    limiter, _, usage = setup()
    try:
        with limiter.workflow(usage, "chat", "failure", "Question"):
            raise RuntimeError("Fake failure")
    except RuntimeError:
        pass
    assert limiter.active == 0 and limiter.reserved == {"generation": 0, "embedding": 0}
    assert limiter.remaining(usage) == 2  # Admitted failures consume session quota.
    with limiter.workflow(new_usage(), "chat", "bounded-calls", "Question", api_budget={"generation": 2}):
        with api_call("generation"):
            pass
        with api_call("generation"):
            pass
        with denied("This request reached the demo's current limits. Please try a simpler question."), api_call("generation"):
            raise AssertionError("Declared workflow budget was exceeded")
    assert len(limiter.calls["generation"]) == 2 and limiter.reserved == {"generation": 0, "embedding": 0}
    with limiter.workflow(new_usage(), "chat", "stale-worker", "Question"):
        stale_context = copy_context()
    with denied(BUSY):
        stale_context.run(lambda: invoke_chat(RunnableLambda(lambda _: None), {}))
    assert limiter.reserved == {"generation": 0, "embedding": 0}


def concurrency_checks():
    limiter, _, _ = setup()
    barrier, release, lock = Barrier(20), Event(), Lock()
    outcomes = []

    def worker(i):
        barrier.wait(timeout=10)
        try:
            with limiter.workflow(new_usage(), "chat", str(i), "Question"):
                assert release.wait(timeout=10)
            return "accepted"
        except UsageLimitError:
            with lock:
                outcomes.append("blocked")
                if len(outcomes) == 18:
                    assert limiter.active == 2
                    release.set()
            return "blocked"

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(worker, range(20)))
    assert results.count("accepted") == 2 and results.count("blocked") == 18
    assert limiter.active == 0 and limiter.reserved == {"generation": 0, "embedding": 0}
    limiter, _, _ = setup(generation_calls_per_minute=5)
    barrier = Barrier(20)

    def api_worker(_):
        barrier.wait(timeout=10)
        try:
            with limiter.api_call("generation"):
                return 1
        except UsageLimitError:
            return 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        assert sum(executor.map(api_worker, range(20))) == 5
    assert len(limiter.calls["generation"]) == 5


def boundary_checks():
    from google.genai import errors
    from workflow import VerifiedEmbeddings, build_workflow, chat_model, run_question
    from verify_conversation import fixtures
    limiter, clock, usage = setup()
    provider = Mock()
    provider.models.embed_content.return_value = SimpleNamespace(embeddings=[SimpleNamespace(values=[0.0] * 3072)])
    adapter = VerifiedEmbeddings(provider)
    retriever, chat, _, _, _ = fixtures()

    def retrieve(question):
        adapter.embed_query(question)
        return retriever.invoke(question)

    from langgraph.checkpoint.memory import InMemorySaver
    with TemporaryDirectory() as temporary, patch.object(rag, "DATA_DIR", Path(temporary)):
        graph = build_workflow(RunnableLambda(retrieve), chat, chat, checkpointer=InMemorySaver())
        for i, question in enumerate(["Tell me about Skardu.", "Tell me about Skardu.", "What's the best season?"]):
            with limiter.workflow(usage, "chat", str(i), question):
                run_question(graph, question, thread_id="controlled-usage-thread")
            clock[0] += 12
        assert len(limiter.calls["generation"]) == 4 and len(limiter.calls["embedding"]) == 2
        assert provider.models.embed_content.call_count == 2
        for call in provider.models.embed_content.call_args_list:
            assert call.kwargs["contents"].startswith("task: search result | query: ")
            assert call.kwargs["config"].output_dimensionality == 3072
            assert call.kwargs["config"].http_options.retry_options.attempts == 1
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder-no-network"}):
        model = chat_model()
        rewriter = chat_model(rewrite=True)
    assert model.max_retries == 1
    assert model.model == "gemini-3.5-flash-lite" and model.max_output_tokens == 1800
    assert rewriter.model == "gemini-3.5-flash-lite" and rewriter.max_output_tokens == 300
    assert rewriter.max_retries == 1
    limiter, clock, usage = setup()
    error = errors.ClientError(429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "private-project-diagnostic"}})
    with patch.object(model.client.models, "generate_content", side_effect=error) as generate:
        with denied(PROVIDER_BUSY), limiter.workflow(usage, "chat", "429", "Question"):
            invoke_chat(model, "Question")
        assert generate.call_count == 1
        assert generate.call_args.kwargs["config"].http_options.retry_options.attempts == 1
    assert limiter.active == 0 and len(limiter.calls["generation"]) == 1
    with denied(BUSY), limiter.workflow(new_usage(), "chat", "after-429", "Question"):
        raise AssertionError("Process backoff did not apply")
    clock[0] += 60
    with limiter.workflow(new_usage(), "chat", "after-backoff", "Question"):
        pass
    rewrite_limiter, _, usage = setup()
    with patch.object(rewriter.client.models, "generate_content", side_effect=error) as generate:
        with denied(PROVIDER_BUSY), rewrite_limiter.workflow(usage, "chat", "rewrite-429", "Question"):
            invoke_chat(rewriter, "Question")
        assert generate.call_count == 1
        assert generate.call_args.kwargs["config"].http_options.retry_options.attempts == 1
    assert rewrite_limiter.daily_calls == {"generation": 1, "embedding": 0}
    assert rewrite_limiter.active == 0


def streamlit_checks():
    from google.genai import errors
    from streamlit.testing.v1 import AppTest
    from verify_conversation import fixtures
    retriever, chat, queries, _, _ = fixtures()
    limiter, clock, _ = setup()
    with patch("workflow.open_retriever", return_value=retriever), patch("workflow.chat_model", return_value=chat), \
            patch("usage_limits.ProcessLimiter", return_value=limiter):
        app = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert not app.exception
        app.chat_input[0].set_value("Tell me about Skardu.").run()
        assert not app.exception and len(queries) == 1
        subject = app.session_state.usage["subject_id"]
        assert limiter.remaining(app.session_state.usage) == 2
        app.run()
        assert len(queries) == 1 and limiter.remaining(app.session_state.usage) == 2
        app.chat_input[0].set_value("What's the best season?").run()
        assert app.info[0].value == COOLDOWN and len(queries) == 1
        app.button(key="clear_chat").click().run()
        assert app.session_state.usage["subject_id"] == subject and limiter.remaining(app.session_state.usage) == 2
        other = AppTest.from_file(str(rag.ROOT / "app.py"), default_timeout=20).run()
        assert other.session_state.usage["subject_id"] != subject and limiter.remaining(other.session_state.usage) == 3
        clock[0] += 12
        failure = errors.ClientError(429, {"error": {"code": 429, "message": "private-project-diagnostic"}})
        with patch("workflow.run_question", side_effect=failure):
            app.chat_input[0].set_value("Tell me about Skardu.").run()
        assert not app.exception and app.error[0].value == PROVIDER_BUSY
        assert "private-project" not in str([x.value for x in app.error])
        assert limiter.active == 0


def main():
    results = {}
    with tracing_context(enabled=False):
        for check in [session_checks, capacity_checks, concurrency_checks, boundary_checks, streamlit_checks, quota_checks]:
            check()
            results[check.__name__] = "pass"
    folder = rag.DATA_DIR / "usage-checks"
    folder.mkdir(exist_ok=True)
    (folder / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    print("All required scenarios passed using fake workflows, fake time, and mocked Gemini; zero real Gemini calls.")


if __name__ == "__main__":
    main()
