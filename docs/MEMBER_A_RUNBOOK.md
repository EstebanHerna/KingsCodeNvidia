# Integrante A: ejecución y entrega a B

La capa de conocimiento se ejecuta desde la raíz del proyecto. El starter pack se conserva sin cambios. El corpus, las descargas y los pesos permanecen fuera de Git mediante `.gitignore`; no se han publicado en la nube.

## Instalación y reproducción

```powershell
python -m venv --system-site-packages .venv
.venv/Scripts/python.exe -m pip install -r requirements-knowledge.txt
.venv/Scripts/python.exe tools/member_a.py reproduce
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe tools/verify_member_a_second.py
```

`reproduce` reconstruye clean, pasajes, grafo y BM25 desde las descargas conservadas; mide las 50 preguntas y valida hashes, contratos, offsets, relaciones y determinismo. Requiere `corpus/raw` y `corpus/acquisition.json`. Para reconstruir también las descargas:

```powershell
.venv/Scripts/python.exe tools/member_a.py acquire
```

La instalación requiere paquetes disponibles o red; la reconstrucción desde raw funciona sin red. Las fuentes pueden actualizarse o desaparecer: reconstrucción idéntica significa usar **el snapshot raw conservado**, con sus hashes. Volver a descargar una versión distinta requiere un nuevo freeze. El comando reutiliza el caché verificado y registra objetivos fallidos; no sustituye una norma inexistente por otra de nombre parecido.

## Interfaz de integración

```python
from kingscode import retrieve
passages = retrieve("¿Qué regula el Código General del Proceso?", k=8, graph_mode="off")

from kingscode import Retriever
retriever = Retriever(mode="bm25", graph_router=router_de_b)
passages = retriever.retrieve(question, k=8, graph_mode="auto")
```

`question` debe ser texto. Rechaza registros con respuestas esperadas. `k=0` y consulta vacía devuelven `[]`; modo desconocido o `k` negativo fallan. El resultado es una copia, ordenada por score, con desempate por `passage_id`. Nunca incorpora campos del banco.

Cada resultado incluye el contrato canónico más `scores` (BM25/dense/RRF/graph/reranker disponibles), `score`, `retrieval` y evidencia del recorrido del grafo. `article` puede ser `null` en sentencias. La procedencia PDF incluye páginas. `text` empieza con la norma y la jerarquía tomada de la fuente, seguida del fragmento literal normalizado. Los offsets son **caracteres Unicode del archivo clean**, no bytes del HTML/PDF; `text_prefix` no forma parte del intervalo.

Para convertir a `pasajes_recuperados` del schema oficial, B debe mapear `text -> texto`, `doc_id -> doc_id` y `score -> score`, preservando la norma incluida en `text`. `inicio`/`fin` son opcionales: si B los usa, debe documentar que señalan el fragmento del clean sin `text_prefix`; no son offsets del HTML original. A no genera `submissions.jsonl` ni modifica respuestas.

## Grafo y routing

El grafo contiene normas/sentencias, secciones, artículos, parágrafos y numerales. `CONTIENE` procede de estructura; `CITA`/`REMITE_A` de referencias explícitas y `MODIFICA`/`DEROGA` solo de patrones inequívocos. No se inventan relaciones para llenar todos los tipos del schema. Nodos externos sin texto tienen `resolved=false`; nunca producen evidencia recuperada.

La expansión recorre un salto, cinco semillas, dos candidatos por vecino y un presupuesto de diez. El router provisional AUTO se activa por expresiones de remisión/modificación/derogación/reglamentación/parágrafo/inciso. Es reemplazable por B. Si AUTO no se activa en el sample, su igualdad con OFF **no demuestra beneficio del grafo**. ON permite medir una ablation forzada.

## Modelos abiertos: siguiente fase GPU

Los dos modelos Qwen de 0,6B están fijados por commit en `config/models.lock.json`. Se verificó una prueba real con dos pasajes oficiales; eso no equivale a un benchmark completo. La máquina actual solo tiene PyTorch CPU. No se instaló CUDA ni se alteró el decoder.

```powershell
# En la máquina objetivo, primero diagnosticar:
python tools/check_cuda.py
# Instalar PyTorch apropiado al diagnóstico y estas dependencias:
.venv/Scripts/python.exe -m pip install -r requirements-neural.txt
.venv/Scripts/python.exe tools/prepare_neural.py --download
```

En la 4090, cambiar explícitamente `config/neural.json` a `device="cuda"`, `dtype="bfloat16"` y un batch apropiado; verificarlo con `tools/neural_smoke.py`. Después:

```powershell
.venv/Scripts/python.exe tools/member_a.py dense
.venv/Scripts/python.exe tools/member_a.py benchmark --mode dense
.venv/Scripts/python.exe tools/member_a.py benchmark --mode hybrid
.venv/Scripts/python.exe tools/member_a.py benchmark --mode hybrid --rerank
```

No hay fallback silencioso si faltan pesos, revisión o índice. El índice denso verifica hashes, orden de pasajes, revisión y configuración. Cambiar la configuración requiere reconstruirlo. Qwen usa pooling del último token, vectores normalizados y consulta con instrucción. El reranker calcula probabilidad `yes/no` con el formato de su model card; no genera respuestas. Se rechazan entradas que excedan el límite en lugar de truncarlas silenciosamente.

Referencias de implementación: [Qwen3 Embedding](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) y [Qwen3 Reranker](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B).

## Límites y tareas de B

- Las fechas y textos son snapshots de la institución; `is_current_text=null` significa vigencia no certificada. Paneles históricos ocultos se conservan en raw, se omiten de clean; bloques explícitos `TEXTO ANTERIOR` quedan marcados y excluidos del índice.
- Los grupos con números de artículo repetidos se excluyen completos mediante `retrieval_eligible=false`. Pueden ser anexos, versiones anteriores o títulos transitorios distintos; se conserva la fuente y no se adivina cuál es canónico. Revisarlos es una tarea explícita de ampliación del corpus.
- Las decisiones se separan por secciones disponibles; no se atribuye automáticamente una ratio ni se distinguen todos los salvamentos de voto.
- `legal_basis` es un proxy ruidoso. Hay etiquetas solo documentales, incompletas y contradictorias. El reporte conserva el original y no lo introduce al índice.
- Recall/MRR son métricas de recuperación, no el puntaje oficial de respuestas. El score end-to-end queda pendiente de B.
- Revisar casos fallidos de adquisición y ambigüedades del parser antes de un freeze competitivo. Conectar el harness, routing y citation guard de B usando exclusivamente la interfaz pública.
- Empaquetar corpus/índice y elegir licencia de procesamiento/enlace público cuando el equipo prepare la entrega; todavía no se ha publicado ni congelado el índice final.
