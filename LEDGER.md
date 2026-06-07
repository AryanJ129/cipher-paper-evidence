# Verification Ledger — Files as Memory, Modes as Principals (draft v0.2, 2026-06-07)

Standalone copy of the paper's Appendix A. Every quantitative claim and citation, with source and status.

Every quantitative claim and every citation, with source and status. **No number in this paper was estimated.** Repo paths are relative to the Cipher repository root. The repository is private at the time of writing: source paths are given as provenance (the audit trail behind each figure), not as public links, and named artifacts can be provided to reviewers on request. The artifacts behind the headline rows, however, are public: the benchmark generator, harness, and raw results, the cited metrics-snapshot rows (verbatim extract), the §6.2 permission config, and this ledger as a standalone file are published at [github.com/AryanJ129/cipher-paper-evidence](https://github.com/AryanJ129/cipher-paper-evidence) (covering rows Q1–Q2, Q4–Q5, Q7, Q9–Q10, Q12, Q27–Q31).

### A.1 Quantitative claims

| # | Claim in paper | Value | Source artifact | Status |
|---|---|---|---|---|
| Q1 | Test suite | 837 passed / 26 skipped (2026-06-06; re-run green 2026-06-07); 829 at the 3.2 close, +8 tests from the four live-verify fixes | `metrics/phase_snapshots.jsonl` (final two lines); `docs/BUILD_LOG.md` | VERIFIED |
| Q2 | Prior full live run | 754 passed / 1 skipped (2026-06-04→05) | `metrics/phase_snapshots.jsonl`; `docs/BUILD_LOG.md` (ambient close) | VERIFIED |
| Q3 | Lens render | ~4.5 ms, live vault (~19 notes), vs 200 ms/500-note trigger | `docs/BUILD_LOG.md` (2.5b close); `CLAUDE.md` | VERIFIED |
| Q4 | Recall latency | 181 ms cold (temporal), 40 ms (scope) | `metrics/phase_snapshots.jsonl` lines 1–2 | VERIFIED |
| Q5 | Classifier latency | 1.95 s/call, async post-reply | `metrics/phase_snapshots.jsonl` line 3 | VERIFIED |
| Q6 | Classifier categories / threshold / telemetry | 8 categories; 0.7 untuned; 71 rows | `backend/src/cipher/classifier/categories.py`; `decisions/decision_log.md` (2026-06-02); `metrics/classifications.jsonl` | VERIFIED |
| Q7 | Cached prefix | 5,390+ tokens cache_read, live; Haiku 4,096-token cache minimum | `metrics/phase_snapshots.jsonl` ("3p1"); `docs/BUILD_LOG.md`; `backend/src/cipher/usage.py` | VERIFIED |
| Q8 | Budget caps | $50 = $15 chat / $25 learning / $5 voice / $5 headroom; warnings 50/75/90% | `backend/src/cipher/usage.py` (`CATEGORY_CAPS`) | VERIFIED |
| Q9 | Per-op costs | classifier ~$0.003; tool turn ~$0.005–0.014; research ~$0.007; STT correct ~$0.002; vision $0.006 | `docs/BUILD_LOG.md` (2.5a, 3p1, P6); `metrics/phase_snapshots.jsonl` | VERIFIED |
| Q10 | Phase spend deltas | $0.00–$0.12 per phase-close verification | `metrics/phase_snapshots.jsonl` (`openrouter_spend_delta` fields) | VERIFIED |
| Q11 | Inference spend | $1.4278 total since key creation (2026-05-26); $1.1300 June month-to-date; Haiku $1.30 / Whisper $0.08 / Sonnet $0.05 / others $0.00 | OpenRouter dashboard, CIPHER key (owner-supplied reading, 2026-06-07) | VERIFIED (dashboard reading; June partial) |
| Q12 | Wake word | 1.52 ms/80 ms frame ≈1.9% one e-core; 8–12% sustained; 0.962 fire score, silence no-fire | `metrics/phase_snapshots.jsonl` (ambient P3/P4); `docs/BUILD_LOG.md` | VERIFIED |
| Q13 | Screen tools | current_context 10 ms; recent_activity 4 ms | `docs/BUILD_LOG.md` (ambient P5) | VERIFIED |
| Q14 | Tool loop bounds | max 4 rounds, final forced prose; 4,000-char result cap | `backend/src/cipher/agent.py` (`_MAX_TOOL_ROUNDS`); `decisions/decision_log.md` (2026-06-04) | VERIFIED |
| Q15 | Recall constants | RRF k=60 equal weights; LOG_WEIGHT 0.5; LOG_CAP 2 | `backend/src/cipher/recall/__init__.py` | VERIFIED |
| Q16 | Gatekeeper | deny-wins fences; $0.25 ask threshold; MAX_SERVERS 6; exact version pins; audit JSONL | `backend/src/cipher/mcp/{manager,permissions,config,audit}.py`; `security audits/2026-06-04_*.md` | VERIFIED |
| Q17 | Fetch-server injected description (verbatim quote) | as quoted in §6 | `security audits/2026-06-04_phase3_part1_mcp_security_review.md` (FINDING 1) | VERIFIED |
| Q18 | CORS finding + closure | wildcard → 3 pinned origins | `security audits/2026-06-03_cipher_security_audit.md` (Finding 001); `…2026-06-04…` §5 | VERIFIED |
| Q19 | Five-query acceptance 5/5; fused-vs-semantic eval | live-verified | `docs/BUILD_LOG.md` (2.5a query surface; recall 1–3) | VERIFIED |
| Q20 | Decision log scale | 40+ entries, append-only | `decisions/decision_log.md` (911 lines) | VERIFIED |
| Q21 | Four live-verify bugs fixed same-day | silent marker reply; AirPods `sd.wait()` wedge; skill-ask gate; stale-snippet legwork answer | `docs/BUILD_LOG.md` (2026-06-06 evening); commits `6429e28`, `d661663`, `ba80821`, `234b34a` | VERIFIED |
| Q22 | Quality gates | ruff / tsc --strict / eslint / next build clean; 0 npm vulns (2026-06-03) | `metrics/phase_snapshots.jsonl`; `docs/BUILD_LOG.md` | VERIFIED |
| Q23 | Vault size at measurement | ~19 notes | `decisions/decision_log.md` (2026-06-03, 2.5b close) | VERIFIED |
| Q24 | VAD segmentation | silero-vad-lite, 512-sample frames, ~0.7 s close, ~20 s cap | `decisions/decision_log.md` (2026-06-02, P2.4) | VERIFIED |
| Q25 | Thermal principle | "cloud-Claude architecturally correct on fanless M3 Air, throttle 8–15 min" | `sources/2026-06-01_cipher_state_document_v4_0.md` (principle 11 + stack table) | VERIFIED (the 8–15 min figure itself is gray-lit [21], labeled) |
| Q26 | Failure-mode names | verification theater; incomplete spec; sycophancy-dropping-objections; scope-explosion relapse | `sources/cipher_self_learning_loop_cc_brief.md` ("Hold objections" §); `sources/2026-06-03_rnd_handoff…md` | VERIFIED |
| Q27 | Recall p50/p95 distributions | resolved by the Q28–Q29 scaling harness (N=30 per size) | `bench/run_scale_benchmark.py` | RESOLVED 2026-06-07 |
| Q28 | Lens-render scaling (SYNTHETIC) | worst-lens p50/p95: 4.7/5.6 ms @19 · 21.3/21.9 @100 · 104.1/109.9 @500 · 247.6/307.2 @1,000; store-backed lenses <1 ms flat | `bench/gen_synthetic_vault.py` + `bench/results/scale_benchmark_2026-06-07.jsonl` | VERIFIED (**synthetic, labeled**) |
| Q29 | Recall scaling (SYNTHETIC) | temporal p95 30.8–40.2 ms, scoped p95 35.3–38.3 ms across 19–1,000 notes | same | VERIFIED (**synthetic, labeled**) |
| Q30 | Index build (SYNTHETIC) | 4.2 s @19 · 7.5 s @100 · 38.1 s @500 · 88.9 s @1,000 | same | VERIFIED (**synthetic, labeled**) |
| Q31 | Dev-tooling permission config (allow/ask split; bypass disabled) | as described in §6.2 | `.claude/settings.json`; commits `7a8e4e6` (2026-05-28) + `ac6b67b` (2026-06-06) | VERIFIED (committed artifact) |
| Q32 | Incident-2 account (late May 2026; laundered-authorization trigger) | §6.2 narrative | owner recollection | OWNER-ATTESTED 2026-06-07; not in a committed file |

### A.2 Citations

| Ref | Status | Note |
|---|---|---|
| [1] Norman 1991 | VERIFIED | pp. 17–38 confirmed; peer-reviewed edited volume |
| [2] LoCoMo, ACL 2024 | VERIFIED | venue corrected to ACL 2024 **main** Long Papers (`2024.acl-long.747`), not Findings |
| [3] Mem0 | VERIFIED w/ correction | arXiv ID confirmed; claimed "ECAI 2025" venue **not verifiable** on arXiv page → cited as preprint |
| [4] mem0 blog 2026 | VERIFIED | staleness quote confirmed verbatim (published 2026-06-05) |
| [5] Letta blog | VERIFIED w/ nuance | 74.0% (gpt-4o-mini, files); 68.5% is Mem0's **graph variant**; phrased precisely in §2.1 |
| [6] SuperLocalMemory | VERIFIED (gray) | author = system's creator; COI noted in the reference |
| [7]–[11] memory preprints | VERIFIED | all five arXiv IDs resolve to the named papers (owner-supplied PDFs in `sources/`) |
| [12] PersonaMem-v2 | VERIFIED | "single, human-readable memory" quote confirmed |
| [13] VerificAgent | VERIFIED | "explicit alignment surface" / "post-hoc human fact-checking pass" / "frozen safety contract" confirmed |
| [14] UI governance | VERIFIED w/ correction | exact title uses "User Interfaces"; "agent memory to be editable" quote confirmed |
| [15] CHI agent memory | VERIFIED w/ correction | venue is **CHI EA '25 Late-Breaking Work** (juried, not a CHI full paper); organization finding phrased as the paper states it (hierarchy/task-based) |
| [16] Externalization review | VERIFIED | also confirms its own use of Norman |
| [17] Personalization survey | VERIFIED | exact title confirmed |
| [18] Agentic-Transparency | VERIFIED (gray) | both gap names verbatim in README; EngrXiv companion preprint located |
| [19] Apple Silicon study | VERIFIED w/ correction | actual scope is **five** runtimes, stated as such |
| [20] On-device review | VERIFIED, claim narrowed | paper exists; the skeleton's "retention/forgetting as future work" claim was **not confirmable from the abstract** → that specific claim is NOT used; cited only as a general on-device-LM survey in §2.4 |
| [21] SolidAITech | VERIFIED (gray) | 8–15 min & 30–50% figures confirmed; article is M5-Air-focused, applied to fanless-Air class; stated as practitioner observation |
| [22] Tom's Hardware | VERIFIED (journalism) | Connatser, 2024-03-09; 114 °C → ~100 °C settle confirmed |
| [23] OWASP Agentic Top 10 | VERIFIED w/ correction | official string is "ASI01 – Agent Goal **Hijack**" (not "Hijacking"); #1 rank confirmed; published 2025-12-09 |
| [24] Invariant Labs | VERIFIED | definition quote confirmed; 2025-04-01 |
| [25] Unit 42 | VERIFIED w/ correction | article at the cited URL is the narrower "…Through MCP **Sampling**" piece; cited for MCP injection vectors generally, **not** for tool-description poisoning (that is [24]) |
| [26] Practical DevSecOps | VERIFIED | "scoped to task, not session" confirmed verbatim |
| [27] OpenClaw incident | VERIFIED, upgraded to primary | cited to the primary trade-press report (TechCrunch, Bort, 2026-02-23; deletion-after-compaction confirmed by direct fetch 2026-06-07). The skeleton's Towards AI piece exists (Moun R., 2026-03-11) but misquotes the incident as "sent" where the documented record is **deletion**; not cited. |
| [28]–[30] siblings | VERIFIED w/ correction | work-buddy "convenient consent" confirmed; obsidian-memory-for-ai "no database…embeddings" confirmed; ChatGPT MD markdown personas confirmed, but two independent verification passes disagreed on its approval depth (one human checkpoint on tool execution vs a "three-layer" reading), so the paper claims only **human-in-the-loop tool approval** |
| [31][32] genre exemplars | VERIFIED (gray) | real posts, dates/URLs confirmed |
| [33] Cormack RRF 2009 | VERIFIED | SIGIR 2009 (carried from the repo's verified source list) |
| [34] OpenJarvis | VERIFIED | project page live (HTTP 200, 2026-06-06) |
| [35] hermes-agent | VERIFIED (gray) | repo exists; the "backpropagation for prompts, not weights" community quote is **paraphrased, not quoted**, in this paper (original reviewer source is low-grade gray lit) |
| DROPPED | — | **ActMem (arXiv:2603.00026)**: paper exists but its abstract does not support the skeleton's "NaiveRAG beats Mem0/A-Mem/MemoryOS" claim → claim and citation removed entirely |
