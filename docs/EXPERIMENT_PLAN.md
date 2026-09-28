# Plan experimental KingsCode v0.5

## Métricas internas
- Recall@1/3/5/10;
- MRR;
- legal_basis@10 cuando sea evaluable;
- cobertura por área/formato;
- Graph OFF vs AUTO;
- validez JSON;
- tasa de citas no respaldadas;
- abstención;
- score oficial;
- RAGAS cuando corresponda;
- latencia p50/p95;
- VRAM pico;
- tiempo proyectado para 992 preguntas.

## Experimentos retrieval — owner A
### R0
BM25.
### R1
Dense Qwen3-Embedding-0.6B.
### R2
BM25 + dense + RRF.
### R3
R2 + Qwen3-Reranker-0.6B.
### R4
R3 + expansión terminológica controlada.
### R5
R4 Graph OFF vs Graph AUTO.
### R6
Chunking estructural vs variante adaptativa, si hace falta.

## Experimentos query/generation — owner B
### G0
Harness + schema validator + citation guard con passages fixture.
### G1
Graph router determinista OFF/AUTO.
### G2
Con retrieval congelado: Qwen3-8B vs ALIA Legal 7B vs Salamandra 7B.
### G3
BF16 vs cuantización solo si VRAM/latencia lo justifican.
### G4
Prompt/abstention tuning manteniendo retrieval y decoder fijos.

## Fine-tuning — condicionado
- retrieval bajo/confusiones: reranker hard-negative FT;
- retrieval alto + generación mala: estudiar QLoRA;
- no entrenar si la mejora no supera baseline de forma reproducible.

## Regla de aceptación
Cada experimento registra config exacta, corpus/graph version, métricas, score, latencia y decisión. Una variable por experimento siempre que sea posible.
