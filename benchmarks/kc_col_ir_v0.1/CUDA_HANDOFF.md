# KC-COL-IR-v0.1 — CUDA handoff

**retrieval_benchmark_ready: true. CUDA_READY: false. Do not execute C0-C3 or CUDA in this freeze.** GOLD_GATE and RANKING_GATE are both unlocked at 10/10. Competitive corpus-v0.1 coverage remains MISSING for all 10 (100%). The separate controlled CUJ 2026 profile contains 6 PDFs, 191 physical pages and 190 passages; all 10 accepted gold mappings resolve. The 30 original items are unchanged; the deterministic next 10 have all been reviewed. Combined dispositions: 10 accepted, 9 pending, 21 rejected. Externado 2011 remains reproducibility-only. Javeriana 2026 remains unparsed and uninspected.

The frozen queue contains an accepted subset and reviewed pending/rejected candidates. Do not substitute benchmark-v1, `kingscode_ir_v2`, Search V2, or Javeriana validation questions. Graph setting for the first future ranking comparison is OFF.

## Frozen handoff inputs

The Git SHA is supplied by the freeze commit and captured in each later run report (do not use a self-referential SHA inside this document).

- Benchmark manifest SHA-256: `2dafdbfb2d863027e6c3ec7fedaa8fe86228dfcaa38197a30d9d85fd994ffe65`
- Accepted DEV gold: `10` (GOLD_GATE: `UNLOCKED`)
- Controlled profile: `KC-COL-IR-CUJ2026-CONTROLLED-v1`; fingerprint `9569be4855bc9223eb346280de21d14b080da8e9b73aa9353175d59345492056`
- Controlled profile document SHA-256: `91fb82825ba61f1f6fc98f2f7a8cc950ea181e1a5e407d7c19fceef41b56f873`
- Controlled runtime manifest SHA-256: `5bcb56f772c6f502d79c41cfef684e61e82b7cd13c7c3c442e35c73730974d3f`
- Corpus path: `tmp/kc_col_ir_v0.1/controlled_cuj2026_v1/` (ignored/local)
- `passages.jsonl` SHA-256: `c942cdfe6ec7f0c88ea0ebe4977540a99b93d98d3404b2972f9609b4499b3a7c`
- BM25 index SHA-256: `277184f3a954de79746589b1e28c932cd2d557bfc2a3e52fe9ab130d7e406a87`; tokenizer `accent-fold-unicode-words-1`; CPU Retriever reopen passed without issuing a query.
- Question-pool SHA-256: `af07237db321115562da4d64527c675d2bb99fe49c730b5f1ebcf2ac3bf85476`; DEV question manifest SHA-256: `4bce1a2257eb23e9ad8db711f1e34cf9184cc42d603dd79542ef8b6527d3e44a`; accepted gold SHA-256: `e4b3786229ece1cd7082179a175e7ee19c5eb0d9173095630074a99fbb2ed0d6`.
- Models lock SHA-256: `ee061a56af47dd4af995b3f57b7fac452054ca15a3e88ee091ebf835ce3c4ec5`. Qwen3-Embedding-0.6B revision: `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`; Qwen3-Reranker-0.6B revision: `e61197ed45024b0ed8a2d74b80b4d909f1255473`.
- Frozen comparison parameters: graph OFF; candidate_k=30; evidence_k=8; metrics_k=10; C0 BM25, C1 Qwen dense, C2 hybrid/RRF, C3 hybrid/Qwen reranker.
- `CUDA_READY=false` because target-runtime handoff checks have not been completed. This does not mean CUDA ran; `cuda_execution_started=false`.

Do not execute the benchmark in this freeze. The dedicated future runner interface is
`python tools/independent_ir_v2.py run --config benchmarks/kc_col_ir_v0.1/runner.json`.
It must use identical questions, corpus, gold, depth and graph OFF for all four
components and write per-question rankings, failure classes, latency and the
required aggregate metrics. The ranking gate and corpus are now verified; this
commit deliberately stops before any C0-C3 execution.

Planned components, after the gate:

- C0: BM25
- C1: Qwen3-Embedding-0.6B dense
- C2: BM25 + dense + RRF
- C3: hybrid + Qwen3-Reranker-0.6B

Required: Evidence Completeness@8, Complete Evidence Set@8, Recall@10,
MRR@10, nDCG@10, Document Recall, Corpus Missing Rate, latency p50/p95,
per-question rankings, and failure classification. No Search V2, benchmark-v1,
or validation tuning.

Current gates: GOLD_GATE 10/10 (UNLOCKED); RANKING_GATE 10/10 (UNLOCKED); retrieval_benchmark_ready=true; CUDA_READY=false; cuda_execution_started=false. Competitive corpus-v0.1 missing rate is 1.0. No C0-C3 retrieval, CUDA, dense retrieval, reranking, or validation inspection was executed in this freeze.
