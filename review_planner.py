"""Three controlled real-model cases; opt-in development traces, no LLM judge."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
from unittest.mock import patch

from langsmith import trace, tracing_context
from langsmith.run_trees import get_cached_client

import rag
from planner import API_BUDGET, PROMPT, RETRIEVAL_MODE, build_planner, run_trip, validate_preferences
from usage_limits import Policy, ProcessLimiter, new_usage
from workflow import chat_model, open_retriever


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", action="store_true", help="Upload only these synthetic development cases to LangSmith.")
    parser.add_argument("--revision", choices=["initial", "revised", "trek-fix", "release-transport"], default="initial")
    parser.add_argument("--case", choices=["trip01", "trip02", "trip03"], help="Recheck only a case with an observed issue.")
    args = parser.parse_args()
    folder = rag.DATA_DIR / "planner-checks"
    folder.mkdir(exist_ok=True)
    output = folder / ("live_results.json" if args.revision == "initial" else f"live_results_{args.revision}.json")
    if output.exists():
        parser.error("Saved results already exist; refusing duplicate Gemini calls.")
    if args.trace and not (os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT")):
        parser.error("Configure private development tracing credentials before --trace.")
    cache = json.loads((rag.DATA_DIR / "query_embeddings.json").read_text(encoding="utf-8"))
    cache_snapshot = folder / "query_cache_before.json"
    if not cache_snapshot.exists():
        cache_snapshot.write_text(json.dumps(
            {key: hashlib.sha256(json.dumps(value).encode()).hexdigest() for key, value in cache.items()}), encoding="utf-8")
    index = folder / "index-snapshot"
    if not index.exists():
        shutil.copytree(rag.DB_PATH, index)
    cases = json.loads((rag.ROOT / "evals/trip_cases.json").read_text(encoding="utf-8"))
    if args.case:
        cases = [case for case in cases if case["id"] == args.case]
    limiter = ProcessLimiter(Policy.from_env())
    report = {"model": rag.CHAT_MODEL, "retrieval": RETRIEVAL_MODE, "development_trace": args.trace,
              "revision": args.revision, "prompt_sha256": hashlib.sha256(PROMPT.messages[0].prompt.template.encode()).hexdigest(),
              "results": [], "api_attempts": {"generation": 0, "embedding": 0}}
    with patch.object(rag, "DB_PATH", index), tracing_context(enabled=False):
        collection = rag.open_collection()
        assert collection.count() == 49
        report["index_vectors"] = 49
        graph = build_planner(open_retriever(mode=RETRIEVAL_MODE), chat_model())
        for case in cases:
            preferences = validate_preferences(case["preferences"])
            record = {**case, "review_status": "needs_manual_review"}
            start = time.perf_counter()
            try:
                with limiter.workflow(new_usage(), "trip_plan", case["id"], "Controlled trip review", api_budget=API_BUDGET):
                    with tracing_context(enabled=args.trace, project_name=os.getenv("LANGSMITH_PROJECT") if args.trace else None):
                        with trace(f"trip-planner-dev-{args.revision}-{case['id']}", inputs={"preferences": preferences},
                                   metadata={"development_only": True, "dataset": "controlled-trip-cases", "case_id": case["id"], "revision": args.revision}) as root:
                            state = run_trip(graph, preferences, trace=args.trace)
                            plan = state["plan"]
                            assert set(plan["cited_ids"]) <= {match["id"] for match in plan["matches"]}
                            record.update(plan=plan, queries=state["queries"], generation_ms=state.get("generation_ms", 0),
                                          trace_url=root.get_url() if args.trace else None, execution_status="pass")
                            root.end(outputs={"status": plan["status"], "cited_ids": plan["cited_ids"]})
            except Exception as error:
                record.update(execution_status="failed", error_type=type(error).__name__)
            record["workflow_ms"] = (time.perf_counter() - start) * 1000
            report["results"].append(record)
            report["api_attempts"] = dict(limiter.daily_calls)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({key: value for key, value in record.items() if key not in {"plan", "preferences"}}, ensure_ascii=True), flush=True)
            if record["execution_status"] == "pass":
                print(json.dumps({key: value for key, value in record["plan"].items() if key != "matches"}, ensure_ascii=True), flush=True)
    if args.trace:
        get_cached_client().flush()
    print(json.dumps({"api_attempts": report["api_attempts"], "index_vectors": 49}))


if __name__ == "__main__":
    main()
