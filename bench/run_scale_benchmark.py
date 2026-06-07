"""Scale benchmark: measure the EXISTING lens + recall code paths against synthetic vaults.

Paper revision pass 2 (2026-06-07). Measures, at vault sizes {19, 100, 500, 1000}:
  - all 8 vault-backed Brain View lens endpoints via FastAPI TestClient (the same
    HTTP render path behind the BUILD_LOG's "~4.5 ms" live figure; the 9th lens,
    Tools, renders from MCP config, not the vault — excluded),
  - recall(): the temporal/date-range path and the person-scoped path,
each warmed once (warmup discarded), then N=30 timed runs -> p50/p95 via
time.perf_counter(). The first post-index call is recorded separately as the
cold figure. Index build time per size is recorded as a bonus metric.

The synthetic vault is generated into a throwaway temp dir (or --workdir) by
bench/gen_synthetic_vault.py — the canonical vault at ~/BRAIN/cipher-vault is
NEVER touched; per-machine runtime stores (staged/trash/MCP audit+config/slots)
are redirected into the workdir, mirroring the test suite's isolation fixture.

Requires Ollama running with nomic-embed-text (real embeddings — the benchmark
measures what the system actually runs; there is no fake embedder).

Output: one JSON line per (size, metric) appended to
  bench/results/scale_benchmark_2026-06-07.jsonl
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bench"))

from gen_synthetic_vault import BASE_DATE, generate  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from cipher import brain, corrections, server, trash  # noqa: E402
from cipher.mcp import audit as mcp_audit  # noqa: E402
from cipher.mcp import config as mcp_config  # noqa: E402
from cipher.recall import recall  # noqa: E402
from cipher.slots import store as slot_store  # noqa: E402
from cipher.staged import queue as staged_queue  # noqa: E402

SIZES = [19, 100, 500, 1000]
N_RUNS = 30
SEED = 42
OUT = (
    REPO / "bench" / "results" / f"scale_benchmark_{date(2026, 6, 7).isoformat()}.jsonl"
)

# The 8 vault-backed lens routes (Tools is MCP-config-backed; not vault-scaling).
LENSES = [
    "/brain/timeline",
    "/brain/commitments",
    "/brain/person/Jenny%20Marlow",
    "/brain/project/atlas",
    "/brain/graph",
    "/brain/review",
    "/brain/trash",
    "/brain/growth",
]


def _isolate(workdir: Path) -> None:
    """Mirror tests/conftest.py: per-machine runtime state -> the throwaway workdir."""
    slot_store._PENDING_DIR = workdir / "pending_tasks"
    staged_queue._STAGED_DIR = workdir / "staged_writes"
    corrections._FILE = workdir / "corrections.json"
    trash._TRASH_DIR = workdir / "brain_trash"
    mcp_audit._LOG_PATH = workdir / "mcp_audit.jsonl"
    mcp_config._CONFIG_PATH = workdir / "mcp_servers.json"


def _pcts(samples_ms: list[float]) -> tuple[float, float]:
    s = sorted(samples_ms)
    p50 = statistics.median(s)
    idx = min(len(s) - 1, max(0, round(0.95 * len(s)) - 1))
    return round(p50, 2), round(s[idx], 2)


def _timed(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000.0


def _machine() -> str:
    try:
        chip = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        chip = platform.processor()
    return f"{chip} / {platform.platform()} / python {platform.python_version()}"


def bench_size(n: int, workdir: Path, out) -> None:
    vault = workdir / f"vault_{n}"
    mix = generate(vault, n, SEED)
    note_count = sum(1 for _ in vault.rglob("*.md"))

    t0 = time.perf_counter()
    brain.init_vault(vault)
    index_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    print(
        f"[size {n}] generated {note_count} notes {mix}; index build {index_ms} ms",
        flush=True,
    )
    out.write(
        json.dumps(
            {
                "size": n,
                "metric": "index_build",
                "ms": index_ms,
                "notes_on_disk": note_count,
                "mix": mix,
            }
        )
        + "\n"
    )

    client = TestClient(
        server.app
    )  # plain client, no lifespan — same as the test suite
    for ep in LENSES:
        cold = _timed(lambda: client.get(ep))  # warmup; recorded as the cold figure
        samples = [_timed(lambda: client.get(ep)) for _ in range(N_RUNS)]
        p50, p95 = _pcts(samples)
        out.write(
            json.dumps(
                {
                    "size": n,
                    "metric": f"lens:{ep}",
                    "p50_ms": p50,
                    "p95_ms": p95,
                    "n": N_RUNS,
                    "cold_ms": round(cold, 2),
                }
            )
            + "\n"
        )
        print(
            f"[size {n}] {ep}: p50 {p50} ms / p95 {p95} ms (cold {cold:.1f})",
            flush=True,
        )

    week = (BASE_DATE - timedelta(days=7), BASE_DATE)
    queries = {
        "recall:temporal": lambda: recall("what did I work on", k=5, date_range=week),
        "recall:scoped": lambda: recall(
            "open items and deadlines", k=5, scope={"person": "Jenny Marlow"}
        ),
    }
    for name, fn in queries.items():
        cold = _timed(fn)  # warmup; recorded as the cold figure
        samples = [_timed(fn) for _ in range(N_RUNS)]
        p50, p95 = _pcts(samples)
        out.write(
            json.dumps(
                {
                    "size": n,
                    "metric": name,
                    "p50_ms": p50,
                    "p95_ms": p95,
                    "n": N_RUNS,
                    "cold_ms": round(cold, 2),
                }
            )
            + "\n"
        )
        print(
            f"[size {n}] {name}: p50 {p50} ms / p95 {p95} ms (cold {cold:.1f})",
            flush=True,
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--workdir",
        type=Path,
        default=None,
        help="throwaway dir for synthetic vaults (default: a temp dir)",
    )
    args = ap.parse_args()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    ctx = (
        tempfile.TemporaryDirectory(prefix="cipher_scale_")
        if args.workdir is None
        else None
    )
    workdir = Path(ctx.name) if ctx else args.workdir
    workdir.mkdir(parents=True, exist_ok=True)
    _isolate(workdir)

    with OUT.open("a", encoding="utf-8") as out:
        out.write(
            json.dumps(
                {
                    "run": "scale_benchmark",
                    "date": "2026-06-07",
                    "seed": SEED,
                    "sizes": SIZES,
                    "n_runs": N_RUNS,
                    "machine": _machine(),
                    "synthetic": True,
                    "note": "synthetic vault per gen_synthetic_vault.py; existing code paths only",
                }
            )
            + "\n"
        )
        for n in SIZES:
            bench_size(n, workdir, out)
            out.flush()
    if ctx:
        ctx.cleanup()
    print(f"\nresults -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
