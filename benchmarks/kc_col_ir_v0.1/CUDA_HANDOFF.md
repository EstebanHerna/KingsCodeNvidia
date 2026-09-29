# KC-COL-IR-v0.1 — CUDA handoff

**CUDA_READY: false. Do not run retrieval or CUDA yet.** GOLD_GATE is unlocked at 10/10 accepted independent DEV gold. Competitive corpus-v0.1 coverage is MISSING for all 10. The separate controlled CUJ 2026 profile has 10 source-page-complete mappings, but its `passages.jsonl` has not been materialized in the worktree, so RANKING_GATE execution remains locked (ranking_n=0 in the manifest). The original 30 item numbers are unchanged; the next 10 deterministic expansion items have all been reviewed. Combined dispositions: 10 accepted, 9 pending, 21 rejected. Externado 2011 is reproducibility-only. Javeriana 2026 remains unparsed and uninspected.

The frozen queue contains an accepted subset and reviewed pending/rejected candidates. Do not substitute benchmark-v1, `kingscode_ir_v2`, Search V2, or Javeriana validation questions. Graph setting for the first future ranking comparison is OFF.

## Required preflight once the gate is met

Fill and freeze every `UNRESOLVED` value below in the handoff commit:

- Git SHA: `UNRESOLVED — regenerate after gold acceptance`
- Benchmark manifest SHA-256: `UNRESOLVED`
- Accepted DEV gold: `10` (GOLD_GATE: `UNLOCKED`)
- Competitive corpus-v0.1 coverage: `10 MISSING`; controlled source-page mapping: `10 COMPLETE`; controlled passage file: `NOT MATERIALIZED` (RANKING execution gate remains locked)
- Corpus profile path: `tmp/kc_col_ir_v0.1/controlled_cuj2026_v1/` (not present in this worktree; build only after handoff review)
- Corpus passages SHA-256: `UNRESOLVED`
- BM25 index SHA-256: `UNRESOLVED`
- Dense index: rebuild with the locked encoder; no compatible frozen index verified
- Model revisions: use exact immutable revisions from `config/models.lock.json`; record them here before execution

Do not execute these placeholders. The dedicated runner interface is
`python tools/independent_ir_v2.py run --config benchmarks/kc_col_ir_v0.1/runner.json`.
It must use identical questions, corpus, gold, depth and graph OFF for all four
components and write per-question rankings, failure classes, latency and the
required aggregate metrics. Until the runner implementation and a >=10-gold
freeze are verified, component commands remain deliberately unavailable.

Planned components, after the gate:

- C0: BM25
- C1: Qwen3-Embedding-0.6B dense
- C2: BM25 + dense + RRF
- C3: hybrid + Qwen3-Reranker-0.6B

Required: Evidence Completeness@8, Complete Evidence Set@8, Recall@10,
MRR@10, nDCG@10, Document Recall, Corpus Missing Rate, latency p50/p95,
per-question rankings, and failure classification. No Search V2, benchmark-v1,
or validation tuning.

Current gates: GOLD_GATE 10/10 (UNLOCKED); controlled source-page mappings 10/10, but passage file not materialized; RANKING_GATE execution 0/10 (LOCKED); CUDA_READY=false. No retrieval, CUDA, neural ranking, or validation inspection was executed during this source-review pass.
