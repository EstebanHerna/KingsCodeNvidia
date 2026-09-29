# KC-COL-IR-v0.1 — CUDA handoff

**CUDA_READY: false. Do not run the independent baseline yet.** There are zero
accepted independent DEV retrieval-gold items; the gate is at least 10. Current primary DEV candidates are JEP-CUJ-2025 (30 from 62 exact official items); Externado 2011 is reproducibility-only. Javeriana 2026 is validation-only and remains unparsed.

The candidate batch is frozen, but it is not gold and is not yet suitable for a score. Do not substitute benchmark-v1, `kingscode_ir_v2`, Search V2, or Javeriana validation questions. Graph setting for the first future comparison is OFF.

## Required preflight once the gate is met

Fill and freeze every `UNRESOLVED` value below in the handoff commit:

- Git SHA: `UNRESOLVED — regenerate after gold acceptance`
- Benchmark manifest SHA-256: `UNRESOLVED`
- Accepted DEV gold: `0` (gate: `>=10`)
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
