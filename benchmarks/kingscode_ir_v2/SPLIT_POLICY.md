# Benchmark v2 split policy

Status: **independent source benchmark not yet populated**. The existing 12-row passage-caption pilot remains a technical smoke fixture, not benchmark evidence and not a tuning target. It was authored from corpus-v0.1 text, and its six DEV rows have already been evaluated once. Validation/holdout pilot files are not a sealed evaluation set.

A competitive item may enter only from a traceable external assessment or a separately documented human-authored source package. Record the issuing body, stable official URL, source hash, source item identifier/page, access date, permitted use, exact source family and review record in source_manifest.jsonl. Do not generate question wording or legal gold with an LLM. Do not derive a quota from desired categories. An inaccessible or unauthenticated source yields zero items.

Assign an entire source family and its duplicate family to exactly one split before retrieval tuning: DEV, VALIDATION, or SEALED_EVAL. Duplicate families include reused item IDs, reprints, translations, near-identical stems, and questions whose operative wording is the same. Keep SEALED_EVAL question text and gold outside the production checkout until a separately authorized final evaluation; store only salted IDs and cryptographic commitments in the exposure ledger meanwhile.

Keep END_TO_END_ONLY items separate from RETRIEVAL_GOLD. The former have a defensible expected answer but no source-level retrieval annotation; exclude them from retrieval metrics. RETRIEVAL_GOLD requires at least one reviewer-verified minimal evidence set. Any one complete set suffices. Gold must refer to verified source passages and must not be supplied to retrieval. Freeze rankings for every item before loading gold.

The current passage-caption pilot is explicitly **not independent**, not selectable, and not evidence about unseen legal questions. Its prior DEV exposure is recorded in reports/benchmark_v2_exposure_log.jsonl. SEALED_EVAL currently has zero eligible items.
