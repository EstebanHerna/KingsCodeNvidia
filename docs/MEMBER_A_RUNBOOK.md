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

## Capa de metadatos y recuperación v0.6

La v0.6 añade una capa de derivación determinista sobre el Corpus v0.1 **sin
cambiar el build ni los hashes del corpus**. Todo es aditivo, opcional y no
altera la ruta por defecto de `retrieve(...)`. El corpus se reconstruye byte a
byte idéntico (mismos hashes de `passages.jsonl`, `graph/*` y `index/bm25.json`).

Módulos nuevos (Integrante A):
- `kingscode/metadata.py`: `canonical_document_id`, `canonical_fragment_id`,
  `content_hash`, `temporal_status`, `document_metadata`, `passage_metadata`,
  `enrich_passage`, `embedding_representation`.
- `kingscode/acquisition_backlog.py`: clasificación de objetivos no resueltos.
- `kingscode/diversify.py`: dedup/diversificación y rasgos de metadatos.
- `kingscode/metadata_experiments.py`: R6/R7/R8.
- `kingscode/failure_analysis.py`: taxonomía de fallos + `document_mismatch_rate`.
- `kingscode/coverage_report.py`: reporte de cobertura v0.6 + auditoría grafo/temporal.

Comandos (CPU, sin GPU):

```powershell
.venv/Scripts/python.exe tools/member_a.py backlog
.venv/Scripts/python.exe tools/member_a.py coverage
.venv/Scripts/python.exe tools/member_a.py failures --mode bm25 --graph-mode off
.venv/Scripts/python.exe tools/member_a.py experiment --experiment-name R6 --question "Ley 1564 de 2012 artículo 391" --mode bm25
```

Reportes generados: `reports/acquisition_backlog_v06.json`,
`reports/corpus_coverage_v06.json`, `reports/retrieval_failures_bm25_<modo>.json`.

### Identidad canónica

`canonical_document_id` y `canonical_fragment_id` son deterministas e
independientes de la URL (misma referencia legal → mismo ID; documento y
fragmento en espacios de nombres separados; variantes históricas y encabezados
repetidos se mantienen distintos). No se infiere validez legal: los campos
temporales usan `unknown`/`null` salvo evidencia explícita. La procedencia
técnica (sha256, ruta, HTTP, timestamp) nunca entra al texto de embedding.

### Scores en tiempo de ejecución

`bm25_score`, `dense_score`, `rrf_score`, `reranker_score`, `graph_score` y
`final_score` son de ejecución y **no** se persisten como metadatos del corpus.

### Pendiente de GPU (4090)

Las variantes neuronales (hybrid + reranker) de R6/R7/R8, el índice denso y el
benchmark neuronal completo siguen siendo exclusivos de la máquina objetivo.
Ejecutar tras `dense`/`benchmark` según la sección GPU anterior; no cambia la
diversificación a activa por defecto sin medición.


## Benchmark interno de retrieval v1

Construir/verificar el benchmark source-derived (no usa `sample_50`):

```powershell
.venv/Scripts/python.exe tools/build_retrieval_benchmark.py --check
.venv/Scripts/python.exe tools/evaluate_retrieval_benchmark.py --variant R0 --split dev
.venv/Scripts/python.exe tools/evaluate_retrieval_benchmark.py --variant R0 --split validation
```

El holdout está protegido. R0 puede usarlo solo como baseline predeclarado:

```powershell
.venv/Scripts/python.exe tools/evaluate_retrieval_benchmark.py --variant R0 --split holdout --allow-holdout --holdout-purpose predeclared_baseline
```

No usar holdout para tuning. El benchmark guarda `questions/` y `gold/` por
separado; el evaluador falla si hashes, schema, snapshot o inputs no coinciden
con el manifest. Para GPU: configurar/validar CUDA, construir el índice Qwen y
ejecutar R1-QWEN/R2-QWEN antes de R3–R8. BGE-M3 requiere una decisión separada
de lock inmutable + loader/index; no usar una revisión no fijada. Consultar
`docs/BENCHMARK_METHODOLOGY.md` y el task board para la secuencia completa.

## Fase vigente: v0.2 CPU tras resultados RTX 4090

Los comandos GPU anteriores quedan como registro histórico, no como siguiente tarea. **No repetir R1–R8, no ajustar validation v1 y no ejecutar su holdout de arquitectura.** Consultar `reports/member_a_v02/gpu_reconciliation.json`. BGE no dispone de lock/loader/index aprobados.

La rama de trabajo es `feat/member-a-corpus-v02-locator`, basada en el freeze 60ebf7e. Copiar el snapshot existente a `corpus/` si se trabaja en otra máquina; no usar acquire/build/reproduce sobre v0.1. Esta sesión no instala CUDA, no carga decoders y no construye dense.

```powershell
python -m unittest discover -s tests -v
python tools/verify_member_a_v02.py
python tools/member_a.py query --question "Ley 1564 de 2012 artículo 90" --mode bm25 --graph-mode off --exact-locator
python tools/benchmark_v2.py check
python tools/benchmark_v2.py dev
python tools/plan_corpus_v02.py
```

El piloto v2 solo comprueba el flujo técnico; sus métricas no seleccionan arquitectura. Revisar el schema, la metodología y la cola humana antes de ampliar casos. `tools/verify_member_a_second.py` reconstruye corpus y repite el sample oficial: no es compatible con las restricciones actuales, por eso se usa la verificación v0.2 que solo lee el snapshot.

### FINAL INTEGRATED RETRIEVAL CANDIDATE

Ablaciones → evidencia de componentes → composición explícita → validation v2 → selección → holdout autorizado → confirmación oficial → freeze top 8. El candidato puede combinar componentes, pero solo tras medir sus interacciones. Exact locator añade candidatos; metadata es soft; graph expansion añade vecinos y graph features puntúa evidencia existente. Dedup conserva provenance y es distinto de diversidad documental. Ninguna de estas opciones se activa por disponibilidad. El artifact de selección debe guardar configuración completa y su fingerprint; el freeze debe coincidir exactamente. Esta fase queda diferida hasta un benchmark v2 revisado, no reabre v1.


## Estado A v0.2 — 2026-09-29

La rama actual preserva el freeze GPU y no reabre v1/Search V2. El piloto v2 previo es técnico y derivado del corpus; no se selecciona arquitectura con él. Consultar docs/MEMBER_A_V02_PROGRESS.md, docs/BENCHMARK_V2_METHODOLOGY.md, benchmarks/kingscode_ir_v2/source_manifest.jsonl y reports/international_sources_v02.json. Hay 0 preguntas independientes de retrieval y 0 SEALED_EVAL. No ejecutar un baseline sobre gold no verificado; primero resolver fuentes externas accesibles, documentar familias duplicadas y revisar gold.
Corpus-v0.2: 4 documentos provisionales; un PDF bloqueado; G02/C01/P02/P01 cuentan con fuentes oficiales preservadas y cinco regresiones focalizadas. G01 y D01 siguen pendientes de revisión. Mantener v0.1 intacto.
