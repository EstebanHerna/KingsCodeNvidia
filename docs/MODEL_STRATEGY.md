# Estrategia de modelos — KingsCode v0.5

## Decoder bakeoff
1. `Qwen/Qwen3-8B` — baseline general fuerte y sugerido por el enunciado.
2. `SINAI/ALIA-es-legal-administrative-7B-Instruct` — candidato especializado en español jurídico/administrativo.
3. `BSC-LT/salamandra-7b-fc-2607` — candidato hispanohablante.
4. `meta-llama/Llama-3.1-8B-Instruct` — control opcional si hay tiempo.

No se decide por reputación: mismo retrieval, passages, prompt, temperatura 0 y evaluador.

## Encoder
Primario: `Qwen/Qwen3-Embedding-0.6B`.
Fallback: `BAAI/bge-m3`.

## Reranker
Primario: `Qwen/Qwen3-Reranker-0.6B`.
Fallback: `BAAI/bge-reranker-v2-m3`.

## Grafo
No es un modelo generativo. A mantiene el grafo y ejecuta expansión; B decide mediante `graph_router` cuándo usar OFF/AUTO/ON. El aporte debe medirse con ablation.

## Cuantización
En RTX 4090 24 GB:
1. probar BF16;
2. reducir precisión solo si la memoria/latencia lo exige;
3. elegir por score + estabilidad + throughput, no solo VRAM.

## Fine-tuning
Decoder: no inicialmente.
Primer candidato: reranker con hard negatives, si el benchmark demuestra confusiones de retrieval.
QLoRA decoder solo si retrieval es alto y persisten errores generativos medibles.
