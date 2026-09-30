# KC-COL-IR pre-CUDA hardening

**Parent:** `main` at `e52816145970adddc70300b1a9988c02b4cd1c8d`

**Purpose:** prepare reproducible diagnostics for the frozen CUJ 2026 controlled profile.

**Execution status:** no retrieval, CUDA, validation, decoder, or GPU benchmark was run for this hardening.

## Frozen inputs and gates

The benchmark manifest and `CUDA_HANDOFF.md` remain the authorities for the
current profile. The accepted set has 10 gold items, all 10 complete in the
controlled 190-passage profile. The competitive corpus v0.1 is missing all ten.
The 30 original CUJ item numbers and deterministic 10-item expansion remain
unchanged. `CUDA_READY` remains false until the target-runtime handoff is
verified. The handoff explicitly stops before C0-C3; this document does not
authorize those runs.

## Hardening contract

| Concern | Contract | Current implementation/status |
|---|---|---|
| Token audit | Count exact pinned Qwen encoder query/document inputs and reranker query-document inputs with local tokenizer files, without model weights or CUDA. Do not claim decoder prompt/context safety before a retrieval freeze. | `tools/audit_kc_col_ir_tokens.py` is prepared; it has not run because the controlled profile is absent from this checkout's ignored `tmp/` directory. |
| Execution identity | Every ranking report records commit, source-tree dirty state (excluding that component's generated report directory), command, Python/platform/package versions, benchmark/config/model-lock/corpus/index hashes, model revisions and verified GPU backend details when applicable. | Added to the independent runner report. A dirty source tree is visible and must be resolved before the freeze run. |
| Candidate@30 | Return and persist the 30-item candidate pool. Report candidate recall, fractional minimal-set coverage and complete minimal-set recovery at 30 independently of Top-8/Top-10 ranking metrics. C3's pool membership is the set presented to its reranker; its order is the reranked order. | Added to the runner. Candidate metrics are diagnostics; the frozen primary metrics remain unchanged. |
| Timing | `initialization_seconds` covers retriever/runtime construction. Each `retrieval_latency_ms` covers one complete synchronous retrieval call; CUDA is synchronized before and after neural calls. Aggregate p50/p95 are query latency. `sum_of_question_retrieval_seconds` is the sum of those calls. `total_wall_seconds` includes runner setup and metric/report preparation. No warmup is hidden (`warmup_queries=0`). | Corrected the misleading historical `initialization_seconds` calculation and made timing fields explicit. |
| RRF identity | `passage_id` is the stable ranked-item identity. A passage can contribute at most once per ranked list; repeated copies in the same list do not add RRF votes. Distinct passage IDs/documents remain distinct even if their text matches. | RRF already de-duplicates repeated integer passage indices per list. The retriever now rejects missing or duplicate indexed `passage_id` values. |
| Duplicate sensitivity | Report repeated passage IDs, repeated fragment IDs, exact normalized-text duplicates, and unique documents within Candidate@30. Preserve every candidate; do not silently deduplicate or merge different source identities. | Added descriptive Candidate@30 diagnostics. This is not a deduplication ablation or a reason to alter the frozen corpus. |
| Shortlist | Use DEV results only to create a shortlist of at most two among C0-C3. First show per-item paired outcomes and descriptive source/topic groups; never tune thresholds or rewrite gold from those outcomes. Rank by `Complete Evidence Set@8`, then `Evidence Completeness@8`, then `Candidate Complete Evidence Set@30`, then `Candidate Recall@30`; exact ties prefer the lower-complexity component in the fixed order C0, C1, C2, C3. Validate the shortlist once on independently acquired and reviewed sources. If no independent validation set is ready, do not select/freeze a winner. | Pre-registered in `docs/experiments/KC_COL_IR_CUJ2026_SHORTLIST_V1.json`. Javeriana 2026 remains unparsed; validation is not ready. |

## CPU token audit command

On a machine holding the exact ignored controlled profile and pinned model
tokenizers, run:

```powershell
python tools/audit_kc_col_ir_tokens.py
```

The script verifies the frozen corpus profile and accepted-question wording,
loads tokenizers from local snapshots only, and writes
`reports/kc_col_ir_v0.1/token_audit.json`. It does not load weights, issue
retrieval queries, or initialize CUDA. If a tokenizer is missing, it fails
closed; it does not download one. An over-limit record blocks the ranking
handoff until the cause is reviewed. No text is silently truncated.

## Remaining handoff

1. Restore the controlled profile and model tokenizers on the target machine;
   run the token audit and inspect any over-limit inputs.
2. Finish the target-runtime diagnostics and snapshot/hash checks required by
   `benchmarks/kc_col_ir_v0.1/CUDA_HANDOFF.md`; keep `CUDA_READY=false` until
   those checks produce versioned evidence.
3. Commit the reviewed hardening changes with a clean tree. This commit becomes
   the execution identity for a separately authorized empirical-ranking phase.
4. Run C0-C3 only in that later phase, after the handoff and current manifest
   explicitly permit ranking. Preserve Candidate@30 lists and per-question
   timings for sensitivity review.
5. Parse and independently review the Javeriana validation family before using
   it. Do not inspect validation performance during DEV shortlist creation.
6. After retrieval selection and freeze, B may run the decoder bakeoff and
   BASE/OPTION/PLAN comparison. The 50 official questions are confirmation only;
   do not retune on them. The synthetic 992 rehearsal is an operations check,
   not evidence of legal-answer quality or real decoder throughput.

The full CPU suite was not run for this hardening, consistent with the existing
instruction to leave execution ready for the target machine.
