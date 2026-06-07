# Evidence bundle — *Files as Memory, Modes as Principals*

Public evidence backing the Verification Ledger of the systems/experience report
**"Files as Memory, Modes as Principals: Lessons from Building a Local-First Personal Agent Without a Framework"**
(Aryan J. Naidu, draft v0.2, 2026-06-07; arXiv link to follow after announcement).

The paper describes Cipher, a single-user personal assistant whose source repository is private.
This bundle publishes the artifacts behind the numbers a reader would most want to check:
the latency and scaling measurements, the prompt-cache and cost figures, the test counts, and
the security-mitigation config. Nothing here is redacted or edited; provenance notes below.

## Contents → which ledger rows they back

| File | What it is | Ledger rows |
|---|---|---|
| `LEDGER.md` | Standalone copy of the paper's full Verification Ledger (Appendix A): 32 quantitative claims + 35 citations, each with source and status | all |
| `bench/gen_synthetic_vault.py` | Synthetic-vault generator: **standalone, stdlib-only, seeded** (same args → byte-identical vault). Emits markdown notes matching the real vault schema; every file is flagged `synthetic: true` | Q28–Q30 |
| `bench/run_scale_benchmark.py` | The measurement harness (lens endpoints via FastAPI TestClient + `recall()`; one discarded warmup, N=30, p50/p95 via `perf_counter`). **Auditable, not externally executable**: it imports the private `cipher` package — included so readers can see exactly what was measured and how | Q27–Q30 |
| `bench/results/scale_benchmark_2026-06-07.jsonl` | Raw benchmark output, unmodified (header line records seed, sizes, N, machine) | Q27–Q30 |
| `phase_snapshots_extract.jsonl` | **Verbatim** extract of the 8 rows the ledger cites from the private repo's `metrics/phase_snapshots.jsonl` (a per-phase build log appended at each phase close). Selection criterion: only rows cited in the ledger; no fields altered | Q1, Q2, Q4, Q5, Q7, Q9 (vision cost), Q10, Q12 |
| `claude_settings.json` | Verbatim copy of the repo's committed `.claude/settings.json` — the two-tier allow/ask permission config that is the mitigation artifact in the paper's §6.2 (committed 2026-05-28 in the private repo, commit `7a8e4e6`) | Q31 |

## Row-by-row quick map

- **Q1/Q2 (test counts 837/26, 829, 754)** → `phase_snapshots_extract.jsonl` rows `3.2-live-verify-fixes`, `3.2-self-learning-loop`, `ambient-p6-p7-close`
- **Q4 (recall 181 ms cold / 40 ms scoped)** → rows `recall_phase4_temporal`, `recall_phase5_scope`
- **Q5 (classifier 1.95 s/call)** → row `2.5a_part1_classifier`
- **Q7/Q10 (5,390 cached tokens; $0.07 phase spend)** → row `3p1-mcp-permissions` (`cache_read_tokens_tool_turns`, `openrouter_spend_delta`)
- **Q9 (vision $0.006/screenshot)** → row `ambient-p6-p7-close`
- **Q12 (wake 0.962 fire score; 8–12% one efficiency core)** → row `ambient-p4-wake-runtime`
- **Q27–Q30 (scaling: lens p50/p95 at 19/100/500/1,000 notes; recall scale-flat; index build)** → `bench/results/*.jsonl`, regenerable inputs via `bench/gen_synthetic_vault.py`
- **Q31 (allow/ask split, bypass disabled)** → `claude_settings.json`

Rows not covered here (e.g. figures sourced to the repo's build log or source files) remain
provenance-only in the ledger; the private artifacts can be shared with reviewers on request.

## Reproducing what can be reproduced

```bash
# the synthetic vault (fully standalone):
python3 bench/gen_synthetic_vault.py /tmp/vault_500 -n 500 --seed 42
```

The measurement harness requires the private `cipher` package plus a local Ollama with
`nomic-embed-text`; it is published for audit, not execution. Machine for all measurements:
Apple M3 MacBook Air (fanless), 16 GB, macOS.

## Provenance statement

- The benchmark results file is the unmodified output of the committed harness (private-repo commit `66097b7`).
- The snapshot extract is verbatim; the only processing was *selection* (ledger-cited rows only).
- `claude_settings.json` is byte-identical to the committed config.
- One honesty note carried over from the paper: all scaling numbers are from **synthetic** vaults
  (schema-matched, labeled); live-usage numbers come from the real ~19-note vault.
