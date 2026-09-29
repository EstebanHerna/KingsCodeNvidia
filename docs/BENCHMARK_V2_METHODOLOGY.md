# Benchmark v2 methodology: current source gate

This benchmark targets unseen Colombian legal questions. Version 1 is closed to tuning. The earlier v2 passage-caption dataset is only a 12-row technical smoke pilot derived from corpus-v0.1 itself. Its six DEV rows were evaluated; the result is not a baseline for unseen questions or architecture selection. It is not independently sourced or authored and is marked TECHNICAL_PILOT_ONLY. The pilot's validation and holdout files are not SEALED_EVAL.

## Source intake

The source manifest records official candidate repositories and retrieval status. As of 2026-09-29, two ICFES direct PDF URLs returned 404. The current ICFES tools page also failed to load in verification. The official SIRNA page confirms an exam guide exists but the crawler did not expose a public item bank. Therefore the independent item count is zero. No question text, gold answers, or expected legal basis were fabricated to fill this gap.

Candidate items require official source identity, stable item/page reference, source hash, access date, use terms, duplicate-family analysis, and split assignment before retrieval tuning. A source with no accessible item text contributes zero benchmark items. External international datasets remain methodological references and cannot supply Colombian legal gold.

## Splits and exposure

Keep source and duplicate families wholly within one split. DEV is for development; VALIDATION is used only after a baseline and failure distribution are frozen; SEALED_EVAL remains outside this checkout until final authorized evaluation. Current SEALED_EVAL count is zero. reports/benchmark_v2_source_duplicates.json audits exact normalized duplicates and family overlap in the legacy pilot only; it does not certify near-duplicate independence. reports/benchmark_v2_exposure_log.jsonl records its prior DEV use.

## Gold records

RETRIEVAL_GOLD records require verified passage evidence and one or more minimal_evidence_sets. Each set is sufficient on its own; completeness is satisfied when every fragment in any one set appears in the frozen ranking. Keep END_TO_END_ONLY answer evidence separate and omit retrieval labels entirely. Retrieval receives the question and eligible textual query views only; rank all questions before loading gold. Do not pass answers, legal bases, or gold IDs to the retriever.

Do not author questions or legal bases with an LLM. Do not use hand-authored quota targets. A human-authored question requires documented external source evidence and independent review. A source-level gold requires citations into primary Colombian or applicable international texts and a recorded reviewer rationale. “Applicable to Colombia” stays unknown unless the ratification/adoption/applicability provenance supports it.

## International cases

A small category may be added only when an externally sourced item genuinely requires retrieval of applicable Colombian-plus-international evidence. Detecting a treaty name alone is insufficient. CAN, ILO, Inter-American and other candidates are tracked in reports/international_sources_v02.json; current international retrieval-gold count is zero. That inventory is a review queue, not an acquisition instruction or legal conclusion.

## Baseline and next action

Do not tune benchmark v1 or rerun Search V2. Once independently sourced DEV items and their retrieval gold exist, first run the current A retrieval stack once without tuning, with exact-locator/graph behavior explicitly frozen and recorded. Report Evidence Completeness@8, Complete Evidence Set@8, Recall@10, MRR@10, nDCG@10, Document Recall, Corpus Missing Rate, latency and the required failure taxonomy. Only that baseline and failure distribution can justify a retrieval experiment. Until then no experiment is evidence-justified.

## Multi-view and graph diagnostics

`kingscode/retrieval_diagnostics.py` provides metric primitives over frozen passage-ID rankings and `minimal_evidence_sets`: Oracle Multi-View Recall takes the union of per-view top-k results; Fusion Loss compares this oracle coverage with the fused ranking; Graph Recovery Rate measures complete-set recovery among questions incomplete before graph expansion. Alternative sufficient sets are evaluated by best-set completeness and are never flattened into a single mandatory union. These are implementation capabilities only: there is currently no independent reviewed DEV set, so there are no empirical scores and no baseline. Rank all views and graph variants before loading gold.
