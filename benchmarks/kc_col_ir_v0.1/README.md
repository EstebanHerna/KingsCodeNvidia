# KC-COL-IR-v0.1

Independent retrieval benchmark from real, source-linked Colombian legal questions. Candidate wording remains local/ignored until rights and exact-text review are complete. Item selection is deterministic and independent of retrieval results.

## Current source roles

- **DEV candidate:** JEP Concurso Universitario, third edition (2025). Its official `/preguntas` page currently exposes 62 clarification-question/response pairs. A deterministic sample of 30 is in the human-review queue. These are not all legal-retrieval questions: some ask for facts, while the JEP explicitly declines to answer some legal/strategic questions. Classify before admitting gold. The current site's 2026 fourth-edition announcement does not make the 2025 question page a 2026 source.
- **VALIDATION candidate:** Javeriana Moot Court Hernán Fabio López / Seguros 2026. One official Q&A PDF was signature/hash checked and stored under ignored `tmp/`; it has not been parsed, scored, or used to tune retrieval. The organizer notes some answers may be inferred from the case or reserved for team analysis, so any later annotation must preserve that distinction.
- **Reproducibility only:** Externado Civil Procedure 2011. Preserve the 270-item pool and its original deterministic sample of 30 in `questions/reproducibility_externado_2011.jsonl`; it is no longer primary DEV.
- **Sealed/discovery:** Externado/Asobancaria moot source (year and source identity require resolution), JEP 2026 questions (not verified on the current question endpoint), and ICFES/SIRNA.

## Integrity and gates

Question text and official responses are stored only in ignored local pools; the Git records contain IDs, provenance, hashes and review state. `gold/dev.jsonl` remains empty. All 30 JEP candidates and the 30 Externado reproducibility records remain unreviewed/temporally uncertain. Baseline and CUDA remain locked until at least 10 independent DEV retrieval-gold packets pass human and primary-source review. Validation data must remain unparsed and uninspected for retrieval performance until the predeclared architecture-selection point.

See `source_manifest.jsonl`, `sampling_manifest.json`, `sampling_manifest_externado_2011.json`, `CUDA_HANDOFF.md` and `docs/DECISION_LOG.md`.
