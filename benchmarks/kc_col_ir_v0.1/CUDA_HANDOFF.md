# KC-COL-IR-v0.1 — CUDA handoff

**CUDA_READY: false. Do not run ranking or CUDA yet.** The GOLD_GATE is 9/10 accepted independent DEV retrieval-gold items. The separate RANKING_GATE is 0/10 accepted gold items with COMPLETE coverage in frozen corpus-v0.1. The CUJ 2026 DEV queue preserves the same 30 source item numbers under the original deterministic sample; no resampling occurred. Seven candidates remain pending and fourteen have rejected dispositions. Externado 2011 is reproducibility-only. Javeriana 2026 is validation-only and remains unparsed.

The frozen queue contains an accepted subset and reviewed pending/rejected candidates. Do not substitute benchmark-v1, `kingscode_ir_v2`, Search V2, or Javeriana validation questions. Graph setting for the first future ranking comparison is OFF.

## Required preflight once the gate is met

Fill and freeze every `UNRESOLVED` value below in the handoff commit:

- Git SHA: `UNRESOLVED — regenerate after gold acceptance`
- Benchmark manifest SHA-256: `UNRESOLVED`
- Accepted DEV gold: `9` (GOLD_GATE: `>=10`)
- Corpus-COMPLETE accepted gold: `0` (RANKING_GATE: `>=10`)
- Corpus path: `corpus/` (historical v0.1 only; verify approved independent-corpus snapshot)
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

Current gates: GOLD_GATE 9/10 (LOCKED); RANKING_GATE 0/10 COMPLETE (LOCKED); CUDA_READY=false. No retrieval or CUDA was executed during this source-review pass.
