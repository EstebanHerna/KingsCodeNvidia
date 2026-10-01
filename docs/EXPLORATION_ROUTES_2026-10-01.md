# Rutas de exploración y mejora — 2026-10-01

## Alcance y estado

Esta nota separa el diagnóstico de la corrida externa en la RTX 4090 de los
cambios preparados en este checkout. En esta sesión no se ejecutaron pruebas,
retrieval, CUDA, generación ni RAGAS; tampoco se adquirieron ni incorporaron
documentos al corpus. El corpus v0.1 y el perfil combinado quedan intactos.

El cambio parte de `93f99a102608dc1cb708ae878e30571653d9c64d` y quedó publicado
en `main` como `495248291ae8e8e3c55a318317345d546b5829ac`. Incluye un parámetro para hacer seleccionable
el presupuesto de expansión del grafo y corregir los contadores del fan-out de
opciones. Esos cambios necesitan revisión y validación en la máquina CUDA antes
de usarlos para comparar calidad o declararlos listos.

## Qué sabemos y qué no

- La corrida externa que se compartió mostró GPU RTX 4090, pesos Qwen presentes
  y fallo de salida JSON en el smoke inicial. Una ejecución posterior de 50
  preguntas apareció activa en los mensajes, pero sus archivos finales no están
  disponibles en este checkout. No se debe inferir su finalización ni sus
  resultados desde la sesión local.
- La respuesta cruda copiada para el smoke parece JSON bien formado, aunque el
  lote la clasificó como `INVALID_MODEL_OUTPUT`. El fragmento compartido no
  incluye el motivo exacto del parser; por eso no atribuyo el fallo a JSON
  sintáctico, citas ni longitud sin inspeccionar `errors/<id>.json`. El parser
  actual guarda ese motivo en la traza de errores y debe preservarse al revisar
  una nueva corrida.
- La corrida híbrida puede gastar muchas evaluaciones del cross-encoder: el
  modo heredado hace una consulta por Q0 y por opción; el router puede pedir una
  segunda pasada con grafo. `retrieval_ms` abarca el tiempo completo, pero los
  contadores por etapa podían reflejar solo la primera vista. La corrección
  local agrega los perfiles de todas las vistas legacy; no cambia ranking,
  contexto ni respuestas.
- El presupuesto de grafo ahora se puede variar entre 0 y 100. `0` desactiva
  expansión de pasajes, pero deja activo el router y sus decisiones. No equivale
  a `graph_policy=off`.
- La cifra `36/41 fully covered` del informe de cobertura es cobertura por
  identificador/documento, no una prueba de que se recupere el pasaje mínimo
  correcto. El mismo inventario deja muchos documentos con vigencia sin
  certificar. Corregir localizadores, segmentación y temporality requiere una
  auditoría por fallo antes de ampliar indiscriminadamente el corpus.
- `full_neural_benchmark_completed` en la estrategia y algunos textos de
  arranque estaban en conflicto con el estado reconciliado del repositorio. No
  se deben presentar el smoke de modelos ni resultados informados por chat como
  un benchmark neuronal versionado.

## Secuencia de experimentos en la 4090

No iniciar un segundo proceso mientras el batch actual esté usando la GPU.
Cuando termine, conservar su carpeta completa, el `identity.json`, los hashes
de corpus/modelo, `batch_report.json`, evaluación oficial, trazas por pregunta
y logs. Primero confirmar que todos los perfiles comparados usen el mismo
commit, corpus, snapshots, entorno y muestra; los tiempos de lote no incluyen
todo el mismo trabajo que el reloj de pared si la inicialización ocurre antes
de `BatchRunner`.

1. **Reproducir una línea base.** Ejecutar el mismo perfil completo de 50
   preguntas en el commit actual y comprobar que el evaluador oficial,
   identidad y replay de ítems terminan correctamente. Mantener prompt,
   precisión, evidencia `k=8`, grafo, corpus y modelo sin cambios.
2. **Piloto de costo, no selector de calidad.** Usar 12 preguntas públicas
   equilibradas (4 por formato) para comparar, cambiando una variable por par:
   fan-out heredado frente a fusión nativa de opciones; `candidate_k=30` frente
   a 15; batch del reranker 2 frente a 1; presupuesto de grafo 10 frente a 0.
   El piloto filtra fallos de JSON/OOM y costo; no elige ganadores de calidad.
3. **Medir la ruta cara por separado.** En los reportes revisar tiempo por
   etapa, número de vistas densas, candidatos y pares/batches del reranker,
   segunda pasada del router, tokens, latencia de generación, VRAM asignada y
   reservada, respuestas válidas, abstenciones por causa y citas por formato.
   No comparar solo el tiempo medio de pregunta. `retrieval_ms` cubre la
   orquestación completa; los perfiles por etapa agregan el trabajo de cada
   llamada, pero no desglosan el costo externo de la fusión RRF de B. Capturar
   `nvidia-smi` al inicio y durante la corrida para distinguir procesos
   concurrentes.
4. **Confirmación con 50.** Repetir baseline y únicamente los perfiles que
   superen el filtro de costo en corridas completas, con evaluación oficial y
   replay en vivo. Elegir por calidad oficial y validez/citación, sujeto al
   límite operativo, no por el piloto ni por RAGAS.
5. **Evaluación secundaria.** Ejecutar RAGAS una sola vez sobre una corrida
   completa seleccionada y su evidencia congelada. Interpretar faithfulness y
   context metrics como estimaciones auxiliares, no como revisión jurídica ni
   prueba de entailment. No mezclar el gasto de esa llamada con los tiempos del
   decoder competitivo.
6. **Cambios de método posteriores.** Si el perfil muestra que domina retrieval,
   probar cache exacta de puntuaciones de reranker o consulta y agrupación por
   longitud como ramas aisladas, midiendo costo y estabilidad del ranking. Si
   domina generación, reducir evidencia solo tras medir cobertura de evidencia
   y score oficial; no introducir continuous batching ni cambiar backend antes
   de tener una línea base estable.

El perfil combinado `v01+v02` sigue siendo diagnóstico cuando sus fuentes v0.1
locales no coinciden byte a byte con el freeze. No usar sus resultados para un
freeze competitivo. No lanzar GPU desde este checkout.

## Propuestas bibliográficas: decisión e implementación optativa

La literatura citada orienta ablations; no anticipa resultados de KingsCode.
Todo lo siguiente conserva las rutas y corpus por defecto. Estas modificaciones
se prepararon para una futura sesión RTX 4090; todavía no se ejecutaron pruebas,
retrieval ni CUDA desde este checkout.

| Propuesta | Estado en KingsCode | Cómo probar / límite |
|---|---|---|
| Contexto estructural tipo SAC-lite | Implementado como `retrieval_text_mode=context`: usa `embedding_representation()` solo en BM25/reranker y un índice denso separado bajo `reports/`. `passage.text`, offsets, citas y corpus v0.1 no cambian. SAC estudió resúmenes sintéticos por documento, no estas cabeceras deterministas ([paper ACL 2025](https://aclanthology.org/2025.nllp-1.3/)). | Comparar `literal` vs `context` con el mismo corpus, instrucción y preguntas. Es metadata determinista, no una réplica del resumen sintético estudiado por SAC. |
| Late Chunking | No implementado. Requiere codificar el contexto documental completo a nivel de tokens y hacer pooling por chunk después del Transformer; anteponer metadatos es otra técnica ([paper](https://arxiv.org/abs/2409.04701)). | No priorizarlo hasta medir SAC-lite. Exigir compatibilidad con el límite de contexto, estrategia de ventanas para documentos extensos e índice denso separado. |
| Instrucciones Qwen separadas | Implementados perfiles optativos distintos para encoder y reranker; el baseline sigue idéntico al lock existente. Se añadieron como primera prueba recomendada `smallest_authoritative_primary_source` y `direct_primary_law_support`, con las instrucciones exactas de la nota del equipo. La instrucción del encoder cambia solo el vector de consulta; no requiere regenerar los vectores de pasaje. Qwen documenta uso de instrucciones ([encoder](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), [reranker](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B)). | Probar por pares y una variable a la vez: baseline vs perfil de encoder; luego baseline vs perfil de reranker. Mantener corpus, índice, retrieval config, preguntas y decoder fijos. Los porcentajes generales del model card no implican ganancia entre dos instrucciones legales concretas. |
| Legal-element query views | La interfaz y el plan congelado ya existían. Se añadió `--plan-roles Q2` para aislar elementos, además de `Q1` hechos y `Q3` vocabulario. Los trabajos relacionados estudian tareas/corpus jurídicos distintos ([KELLER](https://aclanthology.org/2024.emnlp-main.73/), [Elem4LCR](https://aclanthology.org/2024.findings-acl.139/), [LegalSearchLM](https://aclanthology.org/2025.emnlp-main.225/)). | Crear planes una vez solo desde preguntas, guardar hash y replay; las referencias generadas siguen sin privilegios del locator. |
| BGE-M3 denso/sparse/ColBERT | **Pendiente de una preparación segura del modelo.** El snapshot oficial inspeccionado publica `pytorch_model.bin`, mientras el preparador de modelos del repo exige pesos Safetensors y rechaza pickle ([metadata oficial del snapshot](https://huggingface.co/api/models/BAAI/bge-m3); [paper](https://arxiv.org/abs/2402.03216)). No se debilitó esa garantía ni se alteró el lock Qwen. | Primero resolver el artefacto seguro y lock inmutable; luego denso con índice propio, sparse como ablation y ColBERT solo si el costo cabe. No instalar FlagEmbedding en el entorno primario todavía. |
| Soporte condicionado por opción | Implementado como señal auxiliar Qwen-dense `Q + opción` vs top-evidencia final; los scores y tiempo quedan trazados. La opción no se elige automáticamente. | Requiere modo dense/hybrid. Comparar fusión nativa sola vs fusión + señal con la misma corrida/prompt, medir tiempo y revisar cerradas manualmente. Coseno no es entailment. |
| IDs de evidencia | Ya existía en v3: `pasajes_usados` y su validación por IDs; no se duplicó. | Seguir midiendo atribución, sin tratarla como prueba de soporte semántico. |
| JSON restringido | Añadida ruta optativa XGrammar 0.2.8 para Transformers; el proyecto oficial documenta compatibilidad Windows/Python y uso con `LogitsProcessor` ([instalación](https://github.com/mlc-ai/xgrammar/blob/main/docs/start/installation.md), [guía Transformers](https://github.com/mlc-ai/xgrammar/blob/main/docs/start/quick_start.md)). La salida aún pasa el parser v3 y citation guard. La forma/tipos no prueban corrección legal. Cada respuesta usa un procesador nuevo porque la integración HF es stateful/single-use ([código oficial](https://github.com/mlc-ai/xgrammar/blob/main/python/xgrammar/contrib/hf.py)). | `--constrained-json`, dependencia opcional aislada. Primero probar una por formato en Windows/4090; confirmar overhead y salida antes de sample50. |
| Cache exacto de pares reranker | Añadido, apagado por defecto y opt-in con `--reranker-score-cache`. Cache LRU acotado a 8.192 pares, aislado por revisión/modelo/precisión/instrucción y con clave de pregunta+texto de búsqueda. Reutiliza únicamente puntuaciones idénticas dentro del mismo proceso; se reportan pares solicitados, calculados, hits, tokenización y forward GPU. | Comparar apagado vs encendido con mismo corpus y configuración, especialmente router en dos pasadas. Si no hay solapamiento de candidatos, no habrá mejora; no se presupone mejora hasta verla en `batch_report.json`. |
| Hard-negative reranker FT | **Bloqueado por gate de datos.** | No crear trainer hasta tener baseline/freeze, positivos primarios completos, negativos difíciles adjudicados, separación por fuente y test sellado independiente. Nunca entrenar con `sample_50`. |
| RAFT/QLoRA decoder | **Bloqueado por retrieval/data gate.** | Considerar solo con retrieval congelado y fallos generativos residuales demostrados; requiere dataset independiente con evidencia, distractores y evaluación sellada. |

Las implementaciones 1, 2, 3, 5 y 7 son flags/perfiles nuevos y no cambian el
comportamiento por defecto. #4 queda pendiente porque el artefacto oficial no
pasa el contrato seguro de pesos del repo; #6 ya estaba implementado; #8 y #9
siguen pospuestos según los gates. No publicar mejora ni hacer freeze sin la
misma prueba comparativa, reporte versionado, evaluación oficial y revisión de
citas/abstención.

Para aislar las instrucciones recomendadas, usar `--embedding-instruction-profile
smallest_authoritative_primary_source` **o** `--reranker-instruction-profile
direct_primary_law_support`, nunca ambos en la primera pareja. El baseline de
ambos flags es el mismo control congelado. Después de confirmar que cada perfil
arranca, comparar corridas completas con el evaluador oficial; el piloto solo
sirve para detectar fallos de runtime/costo. `late chunking` sigue fuera del
código y no debe confundirse con `retrieval_text_mode=context`.

La cache exacta del reranker es otra ablation optativa: añade
`--reranker-score-cache` y reporta sus hits por pasada. El control mantiene la
cache apagada. Su mayor oportunidad de ahorro es el solapamiento entre la
primera recuperación OFF y la segunda recuperación del router; no se presupone
que exista ni se contabiliza como mejora hasta verlo en `batch_report.json`.

## Corpus: adquisiciones oficiales candidatas

El siguiente backlog proviene de la comparación entre referencias del banco y
el inventario actual. Son fuentes candidatas para un corpus separado v0.2; no
se descargaron aquí. Antes de adquirir, comprobar si el documento completo ya
está en un snapshot externo y revisar vigencia/versiones. Cada adquisición debe
guardar URL y URL final, institución, identidad documental, fecha/hora, bytes y
SHA-256; no sustituir una referencia por otra ni editar v0.1.

| Caso señalado | Fuente oficial candidata | Tratamiento |
|---|---|---|
| q51, q247 | [Ley 472 de 1998 — Función Pública](https://www1.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=188) | Incorporar texto oficial y artículos necesarios en v0.2; verificar versión aplicable. |
| q453 | [C-468/24](https://www.corteconstitucional.gov.co/relatoria/2024/c-468-24.htm), [SU-016/20](https://www.corteconstitucional.gov.co/relatoria/2020/su016-20.htm), [Ley 1774/16](https://www1.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=68135), [Ley 84/89](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=8242) | Revisar periodo jurídico y no confundir Ley 84 con su texto consolidado tras [Ley 2455/25](https://www1.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=259656). |
| q142 | [CE 2020CE-SUJ-4-005, exp. 21329 (PDF)](https://www.consejodeestado.gov.co/sentenciasu/cuarta/10-25000-23-37-000-2013-00443-01%2821329%29SU.pdf) | Incorporar decisión íntegra del Consejo de Estado; el corpus actual no representa esa jurisdicción. |
| q563 | [SU-277/25](https://www.corteconstitucional.gov.co/relatoria/2025/su277-25.htm) | Verificar pasajes/relación con autos de seguimiento. |
| q190 | [T-256/25](https://www.corteconstitucional.gov.co/relatoria/2025/t-256-25.htm) | Revisar hechos y pasaje requerido. |
| q168 | Posible CSJ SC10291-2017 | Identidad probable; texto primario completo aún no localizado. Mantener bloqueada. |
| q272 | Auto Supersociedades 2025-01-730337 | Identidad/URL primaria aún sin resolver. Mantener bloqueada. |

La aparente brecha de q253 parece un problema de mapeo: Ley 1562/12, artículos
56–57 del CST y SL-3385/22 ya figuran en el inventario. Corregir la auditoría de
referencias primero; no re-adquirir sin evidencia de ausencia real.

Para el lote animal, la fuente oficial de Ley 84/89 señala modificaciones por
Ley 2455/25. La fecha del caso decide qué versión es pertinente; una ley
consolidada actual no reemplaza silenciosamente la versión histórica. La
incorporación se acepta solo después de verificar identidad, vigencia,
extracción y pasajes mínimos por una persona.

## Citas, abstención y generación

Mantener el guard y los umbrales actuales durante la comparación inicial. Para
cada abstención, registrar si viene de política de evidencia, salida inválida,
reparación/guardia, error de retrieval o decoder; una sola tasa global no
explica el fallo. Revisar por formato y fuente. El guard comprueba coherencia
legal/estructural de citas y trazabilidad; no determina si toda afirmación está
semánticamente implicada por el pasaje. No ajustar reglas con las 50 preguntas
etiquetadas.

`-CitationFill` y prompt v4 son experimentos posteriores, cada uno con un
control idéntico y una variable. RAGAS no reemplaza al evaluador oficial ni a
una auditoría humana de soporte de afirmaciones. El decoder del concurso debe
seguir determinista y a temperatura cero.

## Prioridad recomendada

1. Completar y preservar la corrida que ya usa la RTX 4090.
2. Corregir los contadores por vistas, sincronizar el commit y hacer el piloto
   pareado con perfil completo.
3. Validar una configuración con la muestra completa y evaluador oficial;
   después, correr RAGAS una vez.
4. Abrir corpus v0.2 para las fuentes oficiales listadas, con trazabilidad y
   temporalidad; revisar fallos del parser antes de activar fuentes/edges.
5. Solo entonces proponer un freeze de retrieval, index o respuestas.
