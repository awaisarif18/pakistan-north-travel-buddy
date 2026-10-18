"""Best-effort public completion counts. Upstash is the only durable authority."""

import argparse
from datetime import date, datetime, timezone
import json
import os
import re
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import UUID

import streamlit as st

NAMESPACE = "north-tours:public-usage:v1"
RETENTION_SECONDS = 30 * 24 * 60 * 60
UNAVAILABLE = "Usage stats temporarily unavailable"
FIELDS = ["questions", "trip_plans", "since"]
INIT = """
if redis.call('EXISTS', KEYS[1]) == 0 then
  redis.call('HSET', KEYS[1], 'questions', 0, 'trip_plans', 0, 'since', ARGV[1])
end
return redis.call('HMGET', KEYS[1], 'questions', 'trip_plans', 'since')
"""
INCREMENT = """
local kind = ARGV[1]
if kind ~= 'questions' and kind ~= 'trip_plans' then return redis.error_reply('Invalid action') end
local totals = redis.call('HMGET', KEYS[1], 'questions', 'trip_plans', 'since')
if not totals[1] or not totals[2] or not totals[3] then return redis.error_reply('Not initialized') end
if not string.match(totals[1], '^%d+$') or not string.match(totals[2], '^%d+$') then
  return redis.error_reply('Invalid totals')
end
local seen = redis.call('GET', KEYS[2])
if seen then
  if seen ~= kind then return redis.error_reply('Action mismatch') end
  return totals
end
redis.call('SET', KEYS[2], kind, 'EX', ARGV[2])
local incremented = redis.pcall('HINCRBY', KEYS[1], kind, 1)
if type(incremented) == 'table' and incremented.err then
  redis.call('DEL', KEYS[2])
  return incremented
end
return redis.call('HMGET', KEYS[1], 'questions', 'trip_plans', 'since')
"""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # Never forward the bearer token to another endpoint.


_HTTP = build_opener(_NoRedirect())


def keys(namespace=NAMESPACE, request_id=None):
    if not re.fullmatch(r"[a-zA-Z0-9:-]{1,120}", namespace):
        raise ValueError("Invalid counter namespace.")
    base = "{" + namespace + "}"
    result = [base + ":totals"]
    if request_id is not None:
        if str(UUID(request_id)) != request_id or UUID(request_id).version != 4:
            raise ValueError("Expected an opaque random request ID.")
        result.append(base + ":done:" + request_id)
    return result


def _command(arguments):
    """One authenticated HTTPS attempt; never log credentials or provider errors."""
    url = os.getenv("UPSTASH_REDIS_REST_URL", "").strip().rstrip("/")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip()
    try:
        parsed = urlparse(url)
        if (not token or parsed.scheme != "https" or not (parsed.hostname or "").endswith(".upstash.io")
                or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path):
            return None
        request = Request(url, data=json.dumps(arguments).encode(), method="POST",
                          headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        with _HTTP.open(request, timeout=3) as response:
            payload = json.loads(response.read(65536))
        return payload.get("result") if isinstance(payload, dict) and not payload.get("error") else None
    except Exception:
        return None


def _stats(values):
    try:
        if not isinstance(values, list) or len(values) != 3:
            return None
        if any(not re.fullmatch(r"[0-9]+", str(value)) for value in values[:2]):
            return None
        since = date.fromisoformat(values[2])
        if since.isoformat() != values[2]:
            return None
        return {"questions": int(values[0]), "trip_plans": int(values[1]), "since": since.isoformat()}
    except (ValueError, TypeError):
        return None


def initialize(*, namespace=NAMESPACE):
    """Explicit rollout operation. Existing totals and start date are never reset."""
    return _stats(_command(["EVAL", INIT, "1", *keys(namespace), datetime.now(timezone.utc).date().isoformat()]))


@st.cache_data(ttl=30, max_entries=1, show_spinner=False)
def read_stats():
    return _stats(_command(["HMGET", *keys(), *FIELDS]))


def record_completion(kind, request_id, *, namespace=NAMESPACE):
    if kind not in FIELDS[:2] or not isinstance(request_id, str):
        return None
    try:
        counter_keys = keys(namespace, request_id)
    except (ValueError, TypeError, AttributeError):
        return None
    return _stats(_command(["EVAL", INCREMENT, "2", *counter_keys, kind, str(RETENTION_SECONDS)]))


def usable_chat(state):
    answer, payload = state.get("answer", {}), state.get("payload", {})
    if not isinstance(answer.get("text"), str) or not answer["text"].strip():
        return False
    if answer.get("answerable") is True:
        return bool(answer.get("cited_ids"))
    # Do not count validation failures that the citation layer turned into refusals.
    return (answer.get("answerable") is False and payload.get("answerable") is False
            and payload.get("paragraphs") == [])


def usable_plan(plan):
    content = [plan.get("overview"), plan.get("transport_alternatives"),
               *plan.get("guidance", {}).values(),
               *[item.get("text") for item in plan.get("days", [])],
               *[item.get("text") for item in plan.get("destination_options", [])]]
    return (plan.get("status") in {"complete", "partial"} and bool(plan.get("cited_ids"))
            and any(isinstance(text, str) and text.strip() for text in content))


def queue_completion(slot, kind, request_id):
    # Local pending delivery metadata only; no duplicate history or visitor identity.
    st.session_state.setdefault("pending_usage_counts", {})[slot] = (kind, request_id)


def render_stats(panel, stats):
    if stats is None:
        panel.html(f'<p class="usage-stats-unavailable">{UNAVAILABLE}</p>')
        return
    since = date.fromisoformat(stats["since"]).strftime("%d %b %Y")
    panel.html('<section class="usage-stats" aria-label="Shared completed requests">'
               f'<div><strong>{stats["questions"]:,}</strong><span>Questions answered</span></div>'
               f'<div><strong>{stats["trip_plans"]:,}</strong><span>Trip plans generated</span></div>'
               f'<p>Counting since {since} · UTC</p></section>')


def sidebar_metrics():
    panel = st.empty()
    render_stats(panel, read_stats())
    return panel


def record_displayed(slot, panel):
    event = st.session_state.get("pending_usage_counts", {}).pop(slot, None)
    if event is None:
        return
    # Consume before writing, even on failure. No automatic write or Gemini retries.
    try:
        stats = record_completion(*event)
    except Exception:
        stats = None
    read_stats.clear()
    render_stats(panel, stats)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).with_name(".env"))
    parser = argparse.ArgumentParser(description="Initialize usage counters once, on the feature's UTC deployment date.")
    parser.add_argument("action", choices=["init"])
    args = parser.parse_args()
    stats = initialize()
    if stats is None:
        raise SystemExit("Counter setup unavailable. Check server-side credentials; existing totals were not reset.")
    print(json.dumps(stats))
