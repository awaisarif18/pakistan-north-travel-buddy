"""Small Gemini boundary hooks; no changes to embeddings or retrieval math."""

from types import SimpleNamespace
from threading import RLock
import json

from google.genai import types

from usage_limits import api_call

EMBEDDING_CACHE_LOCK = RLock()


def protected_embeddings_client(client):
    def embed_content(**kwargs):
        # Per-request override avoids the legacy client's four-attempt retry policy.
        config = kwargs["config"].model_copy(update={
            "http_options": types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=1))})
        token_budget = len(kwargs["contents"].encode("utf-8")) + 256
        with api_call("embedding", input_tokens=token_budget):
            return client.models.embed_content(**{**kwargs, "config": config})
    return SimpleNamespace(models=SimpleNamespace(embed_content=embed_content))


def invoke_chat(chain, inputs):
    # UTF-8 byte count plus headroom for our fixed prompts/schema; no countTokens API call.
    token_budget = len(json.dumps(inputs, ensure_ascii=False).encode("utf-8")) + 4096
    with api_call("generation", input_tokens=token_budget):
        return chain.invoke(inputs)


def completed_payload(response):
    """Never accept a parsed fragment from a token-limited structured response."""
    raw = response.get("raw")
    if raw is None or str(raw.response_metadata.get("finish_reason", "")) != "STOP":
        raise ValueError("The response was incomplete. No partial itinerary or answer was accepted.")
    if response.get("parsing_error") is not None or not isinstance(response.get("parsed"), dict):
        raise ValueError("The response could not be validated. No partial output was accepted.")
    return response["parsed"]
