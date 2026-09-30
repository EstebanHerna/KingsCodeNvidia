# KC-COL-IR-v0.1

Independent retrieval benchmark from real, source-linked Colombian legal questions. Candidate wording remains local/ignored until rights and exact-text review are complete. Item selection is deterministic and independent of retrieval results.

## Current source roles

- **DEV candidate:** JEP Concurso Universitario 2026, fourth edition (SeRVR). The current official `/preguntas` page exposes 62 clarification pairs. The original 30 item numbers remain unchanged; a predeclared deterministic expansion reviewed the next 10. Across 40 reviewed candidates there are 10 accepted gold, 9 pending primary evidence and 21 rejected with recorded reasons. The official 2026 hypothetical packet is acquired and hashed. The official versions page identifies the 2025 third edition as SDSJ; the earlier 2025 ZIP is `NOT_SOURCE_FOR_CUJ_2026_GOLD`.

**Source-page caveat:** the current `/preguntas` page is mixed-edition content and still carries stale “2025 / Tercera Edición” boilerplate. Treat the 30 items as CUJ 2026 only because their case identity and exact materials match the official 2026 packet; the 2025 third-edition SDSJ packet does not match. This correction preserves the original 30 sample IDs/item numbers and does not resample.
- **VALIDATION candidate:** Javeriana Moot Court Hernán Fabio López / Seguros 2026. One official Q&A PDF was signature/hash checked and stored under ignored `tmp/`; it has not been parsed, scored, or used to tune retrieval. The organizer notes some answers may be inferred from the case or reserved for team analysis, so any later annotation must preserve that distinction.
- **Reproducibility only:** Externado Civil Procedure 2011. Preserve the 270-item pool and its original deterministic sample of 30 in `questions/reproducibility_externado_2011.jsonl`; it is no longer primary DEV.
- **Sealed/discovery:** Externado/Asobancaria moot source (year and source identity require resolution), JEP 2026 questions (not verified on the current question endpoint), and ICFES/SIRNA.

## Integrity and gates

Question text and official responses are stored only in ignored local pools; the Git records contain IDs, provenance, hashes and review state. `gold/dev.jsonl` contains 10 accepted independent packets; all 10 are `MISSING` from frozen corpus-v0.1. Across both frozen batches, the 30 original items remain intact and all 10 expansion items have separate dispositions. Gold validity is stored as external evidence units and sets; profile-specific corpus passage IDs are separate mappings. The gold gate is unlocked. The materialized controlled CUJ 2026 profile contains six eligible PDFs, 191 physical pages and 190 page passages; every accepted gold mapping resolves to actual passages, so RANKING_GATE is unlocked at 10/10. `retrieval_benchmark_ready=true`; CUDA remains false until target-runtime handoff checks. No retrieval benchmark has run. Validation data remains unparsed and uninspected.

The separate controlled profile is `KC-COL-IR-CUJ2026-CONTROLLED-v1`: all six eligible textual PDFs from the official ZIP (191 physical pages, 190 nonempty page passages), with source archive SHA-256 `3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101`. Local ignored artifacts include `passages.jsonl`, runtime `manifest.json`, and `index/bm25.json`; their hashes and the corpus fingerprint are recorded in `review/controlled_cuj2026_v1_profile.json`. The mapping and coverage ledgers are in `review/controlled_cuj2026_v1_mapping.jsonl`, `review/controlled_cuj2026_v1_coverage.jsonl`, and `review/competitive_corpus_v01_coverage.jsonl`. CPU build/read verification ran without scoring or querying.

See `source_manifest.jsonl`, `review/jep_2026_dispositions.jsonl`, `review/primary_source_acquisitions.jsonl`, `sampling_manifest.json`, `sampling_manifest_externado_2011.json`, `CUDA_HANDOFF.md` and `docs/DECISION_LOG.md`.
