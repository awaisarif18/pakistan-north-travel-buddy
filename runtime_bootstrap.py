"""Refresh the pre-v1.3 module API during a Streamlit hot update, before app imports."""

import importlib
import sys
from threading import RLock

_LOCK = RLock()


def refresh_legacy_runtime(clear_resources):
    with _LOCK:
        limits = importlib.import_module("usage_limits")
        if callable(getattr(limits, "reserve_additional_calls", None)) and hasattr(getattr(limits, "ProcessLimiter", None), "extend"):
            return False  # Normal reruns must not reset quotas or cached clients.
        importlib.reload(limits)
        for name in ("gemini_protection", "retrieval", "recommendations", "workflow", "planner", "planner_ui", "usage_stats"):
            module = sys.modules.get(name)
            if module is not None:
                importlib.reload(module)
        clear_resources()  # Drop cached instances of the old limiter/workflows once.
        return True


def discard_legacy_conversation(state):
    conversation = state.get("conversation")
    if conversation and "recommend_destinations" not in conversation[1].nodes:
        state.pop("conversation", None)
        state.pop("pending_submission", None)
        # Keep session usage counters and planner results; never reset allowances here.
