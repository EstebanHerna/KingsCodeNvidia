# KC-COL-IR-v0.1

Independent retrieval benchmark from real, source-linked Colombian legal questions. Candidate wording remains local/ignored until rights and exact-text review are complete. Item selection is deterministic and independent of retrieval results.

## Current source roles

- **DEV candidate:** JEP Concurso Universitario 2026, fourth edition (SeRVR). The current official `/preguntas` page exposes 62 clarification pairs. The same 30 source item numbers selected under the original deterministic rule are preserved; only the edition metadata and IDs were corrected, and sampling was not recomputed. Nine items have independently reviewed gold packets, seven remain pending and fourteen are rejected with recorded reasons. The official 2026 hypothetical packet is acquired and hashed. The official versions page identifies the 2025 third edition as SDSJ; the earlier 2025 ZIP is `NOT_SOURCE_FOR_CUJ_2026_GOLD`.

**Source-page caveat:** the current `/preguntas` page is mixed-edition content and still carries stale “2025 / Tercera Edición” boilerplate. Treat the 30 items as CUJ 2026 only because their case identity and exact materials match the official 2026 packet; the 2025 third-edition SDSJ packet does not match. This correction preserves the original 30 sample IDs/item numbers and does not resample.
- **VALIDATION candidate:** Javeriana Moot Court Hernán Fabio López / Seguros 2026. One official Q&A PDF was signature/hash checked and stored under ignored `tmp/`; it has not been parsed, scored, or used to tune retrieval. The organizer notes some answers may be inferred from the case or reserved for team analysis, so any later annotation must preserve that distinction.
- **Reproducibility only:** Externado Civil Procedure 2011. Preserve the 270-item pool and its original deterministic sample of 30 in `questions/reproducibility_externado_2011.jsonl`; it is no longer primary DEV.
- **Sealed/discovery:** Externado/Asobancaria moot source (year and source identity require resolution), JEP 2026 questions (not verified on the current question endpoint), and ICFES/SIRNA.

## Integrity and gates

Question text and official responses are stored only in ignored local pools; the Git records contain IDs, provenance, hashes and review state. `gold/dev.jsonl` contains 9 accepted independent packets; all are `MISSING` from frozen corpus-v0.1. The other 21 candidates remain in the frozen queue with 7 pending primary evidence and 14 rejected dispositions. Gold validity is stored as external evidence units and sets; corpus passage IDs are a separate mapping. The gold gate requires >=10 accepted items; the ranking gate separately requires >=10 `COMPLETE` corpus items. Both ranking and CUDA remain locked. Validation data must remain unparsed and uninspected for retrieval performance until the predeclared architecture-selection point.

See `source_manifest.jsonl`, `review/jep_2026_dispositions.jsonl`, `review/primary_source_acquisitions.jsonl`, `sampling_manifest.json`, `sampling_manifest_externado_2011.json`, `CUDA_HANDOFF.md` and `docs/DECISION_LOG.md`.
