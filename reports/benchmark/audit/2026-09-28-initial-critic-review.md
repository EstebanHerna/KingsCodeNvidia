# Leakage-safe internal retrieval benchmark checkpoint

The change establishes a source-derived internal retrieval benchmark with separate question and gold artifacts, a deterministic builder, a CPU R0 evaluator, and explicit GPU-blocked records for later variants. Retrieval receives only question text and gold loads after rankings are captured; the generated 100-case checkpoint also validates its canonical IDs and spans against the corpus. Template authoring and the review queue avoid closed-model or fabricated semantic questions, while the R0–R8 plan does not claim unavailable GPU results. Watch for: **[confirmed]** a caller can self-authorize any holdout run, empty retrieval results lower the Document Mismatch Rate instead of counting as failures, and recorded benchmark/corpus hashes are not enforced before evaluation. **Verdict**: NEEDS_CHANGES

## High-level view

The benchmark correctly separates retrieval-safe inputs from gold labels and defers label loading until every ranking is complete. The generated checkpoint is deterministic source-locator retrieval rather than semantic question generation; cases requiring semantic or temporal wording are retained outside the scored dataset for human review.

The split builder prevents case and generated-fragment reuse, and the generated 60/20/20 checkpoint passed schema, canonical-ID, span, and split checks. **[confirmed]** Its validator proves referenced IDs resolve in the current corpus but does not establish that the checked question/gold files and corpus are the hash-pinned snapshot named by the manifest.

R0 has a usable CPU path and R1–R8 are represented as pending or GPU-blocked rather than assigned fabricated results. **[confirmed]** The current holdout gate is only an opt-in command-line label, and **[confirmed]** the mismatch metric makes an empty result look better than a wrong top result.

<details>
<summary>Issues (3)</summary>

1. **[confirmed] Holdout authorization is self-attested** — Require a checked predeclaration/selection record (or an immutable allowlist) before accepting `predeclared_baseline` or `post_selection_confirmation`; the present flags alone do not prevent tuning against holdout.
2. **[confirmed] Empty rankings suppress Document Mismatch Rate** — Count an empty ranking as a mismatch, or explicitly exclude and separately report it; returning no rank-1 must not reduce a wrong-document failure metric.
3. **[confirmed] Snapshot hashes are not validated** — In `verify()` and before `run()`, recompute and compare the manifest’s question, gold, and frozen-corpus hashes so results cannot be attributed to a stale manifest.

</details>

<details>
<summary>Details</summary>

## Holdout authorization is self-attested

**[confirmed]** `run()` permits a holdout evaluation whenever the caller supplies `--allow-holdout` and either accepted purpose string. Neither the evaluator nor the CLI reads a predeclared R0 record, a configuration digest, or a completed validation-selection artifact. This leaves the holdout accessible to the same operator who tunes the system; calling the value `predeclared_baseline` does not establish that it was declared before the run. The `record_gpu_blocked()` CLI path can also write a holdout-labelled report without the normal guard, although it does not retrieve questions or emit metrics.

Persist an allowlisted declaration before the run, bind it to the benchmark manifest, split, variant, and configuration hash, and consume it when the holdout report is created. For post-selection confirmation, require a recorded validation-only selection artifact. Cover both accepted purpose paths and rejection of an arbitrary declaration in the tests.

## Empty rankings reduce Document Mismatch Rate

**[confirmed]** `per_question_metrics()` returns `0.0` for `Document Mismatch Rate` when `result` is empty because the value is guarded by `bool(result)`. The methodology defines this as cases whose rank-1 canonical document is not gold; an empty result has no gold rank-1 document and should not improve the score relative to a returned wrong document. An evaluator failure or an empty index can therefore lower the aggregate mismatch rate while Recall, MRR, and completeness correctly fall to zero.

Treat a missing rank-1 as a mismatch, or document a denominator that excludes empty rankings and report the empty-ranking rate alongside it. Add the empty-result case to the hand-verifiable metric tests.

## Manifest identity is recorded but not enforced

**[confirmed]** The builder places SHA-256 values for each question file, gold file, schema, and corpus snapshot in `benchmark_manifest.json`, and runs embed a hash of that manifest plus the current corpus manifest. `verify()` checks only the target total and that current canonical IDs/spans resolve; it never recomputes the declared question/gold/schema or corpus hashes. A later corpus or artifact change that preserves schemas and resolvable IDs can therefore pass `--check`, while a run carries a manifest that describes a different frozen snapshot.

Validate every declared artifact and corpus hash before building a report, fail closed on mismatch, and test an altered question/gold/corpus fixture. This preserves the existing useful provenance fields while making them enforceable.

</details>

<details>
<summary>File map</summary>

- `docs/RETRIEVAL_BENCHMARK_TASK_BOARD.json` — staged RB-00–RB-10 workflow and blocked/pending state.
- `benchmarks/kingscode_ir/README.md` and `benchmark.schema.json` — benchmark boundary, artifact layout, and question/gold contracts.
- `benchmarks/kingscode_ir/{questions,gold,authoring,manifests}/` — generated 100-case checkpoint, separate labels, review queue, and snapshot identity.
- `docs/BENCHMARK_METHODOLOGY.md` — metric, split, holdout, variant, and provenance policy.
- `kingscode/benchmark_builder.py` — deterministic source-template construction and artifact validation.
- `kingscode/retrieval_benchmark.py` — retrieval boundary, metric computation, holdout gate, variant records, and provenance reports.
- `tools/build_retrieval_benchmark.py` and `tools/evaluate_retrieval_benchmark.py` — build/check and evaluation command interfaces.
- `tests/test_retrieval_benchmark.py` — input-boundary, metric, integrity, bootstrap, and variant-registration coverage.

Full diff: `git diff main` plus the untracked benchmark files listed by `git status --short`.

</details>
