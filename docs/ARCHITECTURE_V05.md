# Arquitectura KingsCode v0.5 — Graph-Aware Hybrid RAG

```text
                           QUESTION
                              |
                 +------------+-------------+
                 |                          |
        query normalization          relation signals
                 |                          |
       +---------+---------+                |
       |                   |                |
      BM25              dense               |
       |                   |                |
       +------- RRF -------+                |
               |                            |
            top-N flat                       |
               |                            |
               +------ graph router --------+
                          |
                 OFF / AUTO / ON
                          |
               optional graph expansion
                          |
                     reranker
                          |
                    evidence 6-8
                          |
                  decoder <= 8B
                          |
                 structured JSON
                          |
                   citation_guard
                          |
              supported? -> yes/no
                     |          |
                  deliver    repair/abstain
```

## Layer ownership
- A: corpus, graph, retrieval, reranker inputs and retrieval metrics.
- B: query normalization, graph routing policy, decoder, guards, evaluator, delivery.

## Why graph-aware, not always-on GraphRAG
The graph is part of the data model from ingestion so hierarchy and legal relations are not lost. The query path only expands the graph when it is likely to add relevant evidence. Direct factual retrieval remains on the lower-latency fast path.

## Interfaces
### Retrieval
```text
retrieve(question, k=8, graph_mode="auto") -> passages
```

### Answer
```text
answer(question, passages, format) -> submission_row
```

## Quality gates
1. retrieval coverage first;
2. citation support second;
3. decoder quality third;
4. latency/reproducibility always measured.

## Implemented baseline
Member A's local backend is BM25 with 30 internal candidates and 8 returned passages by default (10 for retrieval evaluation). Dense/RRF/reranker paths are implemented; the full neural benchmark remains pending on the target GPU. Corpus v0.1 contains only official source text, excludes historical/ambiguous article groups from retrieval, and retains them for audit. See `MEMBER_A_RUNBOOK.md` and `../CORPUS.md` for measured status rather than treating the target architecture as an already benchmarked full pipeline.
