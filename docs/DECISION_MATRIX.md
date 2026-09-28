# Matriz de decisiones — antes de CUDA

Las probabilidades son **priors de planificación**, no resultados de benchmark. Se actualizan en cuanto corramos `sample_50`.

## División del equipo
| Opción | Probabilidad de ser la mejor | Motivo |
|---|---:|---|
| Por subsistemas (Corpus/Retrieval vs Inference/Eval) | 70% | paraleliza trabajo y reduce conflictos |
| Por áreas jurídicas | 15% | duplica tooling y dificulta integración |
| Ambos full-stack alternando tareas | 15% | flexible, pero genera cuellos de botella |

## Retrieval
| Opción | Probabilidad | Comentario |
|---|---:|---|
| BM25 + Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B | 60% | mejor equilibrio precisión/VRAM/latencia |
| BM25 + BGE-M3 + Qwen3-Reranker-0.6B | 30% | muy fuerte y robusto en multilingüe |
| Solo dense embeddings | 10% | débil para artículos, números y nombres exactos |

## Decoder
| Opción | Probabilidad | Comentario |
|---|---:|---|
| Qwen3-8B | 55% | razonamiento, multilingüe, instruction following, licencia permisiva |
| Salamandra-7b-fc-2607 | 30% | español + mejora reciente de instruction following |
| Llama-3.1-8B-Instruct | 15% | baseline sólido, pero menos atractivo para este dominio |

## Fine-tuning
| Opción | Probabilidad de mejor ROI | Comentario |
|---|---:|---|
| Sin FT del decoder; optimizar RAG | 65% | 50 ejemplos son pocos; retrieval domina el reto |
| Fine-tune del reranker | 25% | barato y directamente relevante |
| QLoRA del decoder | 10% | solo si el error dominante es generación/formato |
