"""Fake-clock checks for model-specific budgets and Pacific calendar days."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from zoneinfo import ZoneInfo

from usage_limits import BUSY, DAILY_LIMIT, Policy, ProcessLimiter, UsageLimitError, api_call, new_usage


def quota_checks():
    clock = [10000.0]
    wall = [datetime.fromisoformat("2026-10-17T12:00:00+00:00")]
    limiter = ProcessLimiter(Policy(), clock=lambda: clock[0], wall_clock=lambda: wall[0])

    def denied(expected, operation):
        try:
            operation()
        except UsageLimitError as error:
            assert str(error) == expected
        else:
            raise AssertionError("Quota did not block the operation")

    def call(target, kind, **kwargs):
        with target.api_call(kind, **kwargs):
            pass

    # Actual generation attempts, not messages or admission reservations.
    for i in range(300):
        with limiter.workflow(new_usage(), "chat", str(i), "Question", api_budget={"generation": 1}):
            with api_call("generation"):
                pass
        clock[0] += 61
    assert limiter.daily_calls["generation"] == 300
    denied(DAILY_LIMIT, lambda: call(limiter, "generation"))
    call(limiter, "embedding")
    assert limiter.daily_calls == {"generation": 300, "embedding": 1}

    # Unused reservations are returned and never charged to daily attempts.
    fresh = ProcessLimiter(Policy(), clock=lambda: clock[0], wall_clock=lambda: wall[0])
    with fresh.workflow(new_usage(), "chat", "unused", "Question"):
        pass
    assert all(value == 0 for value in fresh.daily_calls.values())
    assert all(value == 0 for value in fresh.reserved.values())
    for _ in range(10):
        call(fresh, "generation")
    denied(BUSY, lambda: call(fresh, "generation"))
    clock[0] += 60
    call(fresh, "generation")

    # Chat and future planning consume the same generation budget.
    shared = ProcessLimiter(Policy(generation_calls_per_day=3), clock=lambda: clock[0])
    with shared.workflow(new_usage(), "chat", "answer", "Question", api_budget={"generation": 1}):
        with api_call("generation"):
            pass
    with shared.workflow(new_usage(), "trip_plan", "plan", "Fake plan", api_budget={"generation": 2}):
        for _ in range(2):
            with api_call("generation"):
                pass
    assert shared.daily_calls["generation"] == 3
    denied(DAILY_LIMIT, lambda: call(shared, "generation"))

    # Embedding minute/day/input budgets are independent of text generation.
    isolated = ProcessLimiter(Policy(embedding_calls_per_minute=1, embedding_calls_per_day=2,
                                     embedding_input_tokens_per_minute=10), clock=lambda: clock[0])
    denied(BUSY, lambda: call(isolated, "embedding", input_tokens=11))
    assert isolated.daily_calls["embedding"] == 0
    call(isolated, "embedding", input_tokens=10)
    denied(BUSY, lambda: call(isolated, "embedding"))
    call(isolated, "generation")
    clock[0] += 60
    call(isolated, "embedding")
    clock[0] += 60
    denied(DAILY_LIMIT, lambda: call(isolated, "embedding"))
    token_limiter = ProcessLimiter(Policy(generation_input_tokens_per_minute=10), clock=lambda: clock[0])
    call(token_limiter, "generation", input_tokens=6)
    denied(BUSY, lambda: call(token_limiter, "generation", input_tokens=5))
    clock[0] += 60
    call(token_limiter, "generation", input_tokens=5)

    # Pacific midnight, not UTC midnight or a fixed UTC offset, resets daily attempts.
    for start, transition, midnight, hours in [
        ("2026-03-08T08:00:00+00:00", "2026-03-08T10:01:00+00:00", "2026-03-09T07:00:00+00:00", 23),
        ("2026-11-01T07:00:00+00:00", "2026-11-01T09:01:00+00:00", "2026-11-02T08:00:00+00:00", 25),
    ]:
        wall[0] = datetime.fromisoformat(start)
        daily = ProcessLimiter(Policy(generation_calls_per_day=1), clock=lambda: clock[0], wall_clock=lambda: wall[0])
        call(daily, "generation")
        wall[0] = datetime.fromisoformat(transition)
        clock[0] += 61
        denied(DAILY_LIMIT, lambda: call(daily, "generation"))
        end = datetime.fromisoformat(midnight)
        assert (end - datetime.fromisoformat(start)).total_seconds() == hours * 3600
        wall[0] = end - timedelta(seconds=1)
        denied(DAILY_LIMIT, lambda: call(daily, "generation"))
        wall[0] = end
        call(daily, "generation")
        assert daily.day == end.astimezone(ZoneInfo("America/Los_Angeles")).date()
        assert daily.daily_calls["generation"] == 1

    # A workflow admitted before midnight keeps its outstanding reservation afterward.
    wall[0] = datetime.fromisoformat("2026-10-18T06:59:59+00:00")
    crossing = ProcessLimiter(Policy(generation_calls_per_day=1), clock=lambda: clock[0], wall_clock=lambda: wall[0])
    with crossing.workflow(new_usage(), "chat", "crossing", "Question", api_budget={"generation": 1}):
        wall[0] += timedelta(seconds=1)
        denied(DAILY_LIMIT, lambda: call(crossing, "generation"))
        with api_call("generation"):
            pass
    assert crossing.daily_calls["generation"] == 1 and crossing.reserved["generation"] == 0

    # Daily admission is atomic too, even with independent simultaneous callers.
    race = ProcessLimiter(Policy(generation_calls_per_minute=100, generation_calls_per_day=5))
    barrier = Barrier(20)

    def worker(_):
        barrier.wait(timeout=10)
        try:
            call(race, "generation")
            return 1
        except UsageLimitError:
            return 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        assert sum(executor.map(worker, range(20))) == 5
    assert race.daily_calls["generation"] == 5


if __name__ == "__main__":
    quota_checks()
    print("Model budgets, daily races, midnight reservations, and 23/25-hour Pacific days passed. No API calls.")
