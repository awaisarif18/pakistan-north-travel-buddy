"""Volatile anonymous quotas and process-local workflow/API admission."""

from collections import deque
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from threading import RLock
import time
from uuid import uuid4
from zoneinfo import ZoneInfo


BUSY = "The travel assistant is busy right now. Please try again shortly."
PROVIDER_BUSY = "Gemini is temporarily at capacity. Please try again later."
QUOTA = "You've reached the current demo usage limit. Please try again later."
COOLDOWN = "Please wait a few seconds before sending another question."
UNCONFIGURED = "The travel assistant is temporarily unavailable. Please try again later."
DAILY_LIMIT = "The demo has reached its shared daily allowance. Please try again later."
KINDS = ("generation", "embedding")


class UsageLimitError(Exception):
    """Contains only a message safe to show to anonymous visitors."""


@dataclass(frozen=True)
class Policy:
    chat_requests: int = 3
    trip_requests: int = 1
    window_seconds: int = 3600
    cooldown_seconds: int = 12
    question_chars: int = 700
    concurrent_workflows: int = 2
    workflows_per_minute: int | None = 3
    generation_calls_per_minute: int | None = 10
    generation_calls_per_day: int = 300
    embedding_calls_per_minute: int | None = 30
    embedding_calls_per_day: int = 300
    generation_input_tokens_per_minute: int = 150000
    embedding_input_tokens_per_minute: int = 20000
    provider_backoff_seconds: int = 60

    def __post_init__(self):
        for name, value in vars(self).items():
            minimum = 0 if name == "cooldown_seconds" else 1
            if value is not None and (not isinstance(value, int) or value < minimum):
                raise ValueError(f"Invalid usage configuration: {name}.")

    @classmethod
    def from_env(cls):
        fields = {"CHAT_REQUESTS_PER_WINDOW": "chat_requests", "TRIP_REQUESTS_PER_WINDOW": "trip_requests",
                  "USAGE_WINDOW_SECONDS": "window_seconds", "SUBMISSION_COOLDOWN_SECONDS": "cooldown_seconds",
                  "MAX_QUESTION_CHARS": "question_chars", "MAX_CONCURRENT_WORKFLOWS": "concurrent_workflows",
                  "WORKFLOWS_PER_MINUTE": "workflows_per_minute", "GENERATION_API_CALLS_PER_MINUTE": "generation_calls_per_minute",
                  "EMBEDDING_API_CALLS_PER_MINUTE": "embedding_calls_per_minute",
                  "GENERATION_API_CALLS_PER_DAY": "generation_calls_per_day",
                  "EMBEDDING_API_CALLS_PER_DAY": "embedding_calls_per_day",
                  "GENERATION_INPUT_TOKENS_PER_MINUTE": "generation_input_tokens_per_minute",
                  "EMBEDDING_INPUT_TOKENS_PER_MINUTE": "embedding_input_tokens_per_minute",
                  "PROVIDER_BACKOFF_SECONDS": "provider_backoff_seconds"}
        return cls(**{field: int(os.environ[key]) for key, field in fields.items() if os.getenv(key, "").strip()})


def new_usage(subject_id=None):
    # Subject identity is separate from the conversation/thread, so clearing chat cannot reset quotas.
    return {"subject_id": subject_id or str(uuid4()), "events": {"chat": deque(), "trip_plan": deque()},
            "last_admitted": None, "seen": {}}


_CURRENT_LIMITER = ContextVar("current_usage_limiter", default=None)


def is_rate_limit(error):
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        if (getattr(error, "code", None) == 429 or getattr(error, "status_code", None) == 429
                or getattr(error, "status", None) == "RESOURCE_EXHAUSTED"
                or type(error).__name__ in {"GoogleRateLimitError", "ResourceExhausted", "TooManyRequests"}):
            return True
        error = error.__cause__ or error.__context__
    return False


class ProcessLimiter:
    def __init__(self, policy, clock=time.monotonic, wall_clock=lambda: datetime.now(timezone.utc)):
        self.policy, self.clock = policy, clock
        self.wall_clock = wall_clock
        self.quota_timezone = ZoneInfo("America/Los_Angeles")
        self.lock = RLock()
        self.active = 0
        self.workflows = deque()
        self.calls = {kind: deque() for kind in KINDS}
        self.tokens = {kind: deque() for kind in KINDS}
        self.reserved = dict.fromkeys(KINDS, 0)
        self.daily_calls = dict.fromkeys(KINDS, 0)
        self.day = None
        self.blocked_until = 0.0

    @staticmethod
    def _prune(events, now, window):
        while events and events[0] <= now - window:
            events.popleft()

    def remaining(self, usage, action="chat"):
        with self.lock:
            events = usage["events"][action]
            self._prune(events, self.clock(), self.policy.window_seconds)
            limit = self.policy.chat_requests if action == "chat" else self.policy.trip_requests
            return max(0, limit - len(events))

    def _capacity(self, kind, now, additional):
        day = self.wall_clock().astimezone(self.quota_timezone).date()
        if day != self.day:
            self.day = day
            self.daily_calls = dict.fromkeys(KINDS, 0)
        # Outstanding reservations survive midnight and still consume headroom.
        if self.daily_calls[kind] + self.reserved[kind] + additional > getattr(self.policy, f"{kind}_calls_per_day"):
            raise UsageLimitError(DAILY_LIMIT)
        cap = getattr(self.policy, f"{kind}_calls_per_minute")
        if cap is None:
            raise UsageLimitError(UNCONFIGURED)
        self._prune(self.calls[kind], now, 60)
        if len(self.calls[kind]) + self.reserved[kind] + additional > cap:
            raise UsageLimitError(BUSY)

    @contextmanager
    def workflow(self, usage, action, request_id, text, *, api_budget=None):
        if action not in {"chat", "trip_plan"}:
            raise ValueError("Unknown usage action.")
        if not text.strip() or len(text) > self.policy.question_chars:
            raise UsageLimitError(f"Please enter a question of 1 to {self.policy.question_chars} characters.")
        if api_budget is None and action == "trip_plan":
            raise ValueError("Future trip workflows must declare their bounded API-call budget.")
        budget = {**dict.fromkeys(KINDS, 0), **(api_budget if api_budget is not None else {"generation": 2, "embedding": 1})}
        if set(budget) != set(KINDS) or any(not isinstance(n, int) or n < 0 for n in budget.values()):
            raise ValueError("Invalid API-call reservation.")
        with self.lock:
            now = self.clock()
            usage["seen"] = {key: stamp for key, stamp in usage["seen"].items() if stamp > now - self.policy.window_seconds}
            if request_id in usage["seen"]:
                raise UsageLimitError("This question has already been submitted.")
            if self.remaining(usage, action) == 0:
                raise UsageLimitError(QUOTA)
            if usage["last_admitted"] is not None and now - usage["last_admitted"] < self.policy.cooldown_seconds:
                raise UsageLimitError(COOLDOWN)
            budgets = (self.policy.workflows_per_minute, self.policy.generation_calls_per_minute,
                       self.policy.embedding_calls_per_minute)
            if any(value is None for value in budgets):
                raise UsageLimitError(UNCONFIGURED)
            self._prune(self.workflows, now, 60)
            if (now < self.blocked_until or self.active >= self.policy.concurrent_workflows
                    or len(self.workflows) >= self.policy.workflows_per_minute):
                raise UsageLimitError(BUSY)
            for kind in KINDS:
                self._capacity(kind, now, budget[kind])
            for kind in budget:
                self.reserved[kind] += budget[kind]
            self.active += 1
            self.workflows.append(now)
            usage["events"][action].append(now)
            usage["last_admitted"] = now
            usage["seen"][request_id] = now
        reservation = {"remaining": budget, "active": True}
        token = _CURRENT_LIMITER.set((self, reservation))
        try:
            yield
        finally:
            _CURRENT_LIMITER.reset(token)
            with self.lock:
                reservation["active"] = False
                self.active -= 1
                for kind in budget:
                    self.reserved[kind] -= budget[kind]  # Release unused reservations, not spent calls.

    @contextmanager
    def api_call(self, kind, reservation=None, *, input_tokens=0):
        with self.lock:
            now = self.clock()
            if now < self.blocked_until:
                raise UsageLimitError(BUSY)
            self._capacity(kind, now, 1 if reservation is None else 0)
            token_events = self.tokens[kind]
            while token_events and token_events[0][0] <= now - 60:
                token_events.popleft()
            if sum(count for _, count in token_events) + input_tokens > getattr(self.policy, f"{kind}_input_tokens_per_minute"):
                raise UsageLimitError(BUSY)
            if reservation is not None:
                if not reservation["active"]:
                    raise UsageLimitError(BUSY)
                remaining = reservation["remaining"]
                if remaining[kind] <= 0:
                    raise UsageLimitError("This request reached the demo's current limits. Please try a simpler question.")
                remaining[kind] -= 1
                self.reserved[kind] -= 1
            self.calls[kind].append(now)  # Attempts, including failures, consume capacity.
            self.daily_calls[kind] += 1
            token_events.append((now, input_tokens))
        try:
            yield
        except Exception as error:
            if is_rate_limit(error):
                with self.lock:
                    self.blocked_until = max(self.blocked_until, self.clock() + self.policy.provider_backoff_seconds)
                raise UsageLimitError(PROVIDER_BUSY) from None
            raise


@contextmanager
def api_call(kind, *, input_tokens=0):
    current = _CURRENT_LIMITER.get()
    if current is None:
        yield  # Explicit local CLI/evaluation calls are not anonymous application traffic.
    else:
        limiter, reservation = current
        with limiter.api_call(kind, reservation, input_tokens=input_tokens):
            yield


def question_limit():
    current = _CURRENT_LIMITER.get()
    return current[0].policy.question_chars if current is not None else Policy().question_chars
