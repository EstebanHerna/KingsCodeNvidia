# Revisiones y acceso — Gate 2-Prep

Metadatos obtenidos de la API y los repositorios oficiales de Hugging Face el 2026-09-28. Solo se consultaron metadatos, model cards, configuración pública y licencias; **no se descargaron pesos de decoders**. Evidencia de consulta y hashes de documentos en `reports/gate2_prep/model_sources.json`.

| Alias | Repositorio | Commit inmutable | Licencia declarada | Acceso observado |
|---|---|---|---|---|
| qwen3-8b | Qwen/Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218` | Apache-2.0 | Público |
| alia-legal-7b | SINAI/ALIA-es-legal-administrative-7B-Instruct | `4215a455e668d033bfd7cf34c358cbb62ae20514` | Apache-2.0 | Público |
| salamandra-7b | BSC-LT/salamandra-7b-fc-2607 | `6d4fe322555ae6f35a90f9077f526886b075fdb5` | Apache-2.0 | Aprobación manual |
| llama31-8b | meta-llama/Llama-3.1-8B-Instruct | `0e9e39f249a16976918f6564b8830bc894c89659` | Llama 3.1 Community License | Aprobación manual; opcional deshabilitado |

Fuentes de licencia fijadas a esos commits: [Qwen LICENSE](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/LICENSE), [ALIA model card](https://huggingface.co/SINAI/ALIA-es-legal-administrative-7B-Instruct/blob/4215a455e668d033bfd7cf34c358cbb62ae20514/README.md), [Salamandra model card](https://huggingface.co/BSC-LT/salamandra-7b-fc-2607/blob/6d4fe322555ae6f35a90f9077f526886b075fdb5/README.md), [Llama LICENSE](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/0e9e39f249a16976918f6564b8830bc894c89659/LICENSE). ALIA y Salamandra declaran Apache-2.0 en sus cards; no se encontró un archivo `LICENSE` independiente en esos snapshots. Llama también exige revisar su política de uso; no se etiqueta como Apache.

Los endpoints de configuración/tokenizer de Salamandra y Llama devolvieron HTTP 401 sin autenticación. Eso se conserva como **acceso no verificado**, no como indisponibilidad definitiva. El titular de la cuenta debe solicitar acceso y aceptar los términos correspondientes; los comandos no realizan esa aceptación. Una cuenta sin autorización obtiene un fallo explícito, nunca otro modelo.

Los locks previos se conservan exactamente como entradas:

- Qwen/Qwen3-Embedding-0.6B: `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`.
- Qwen/Qwen3-Reranker-0.6B: `e61197ed45024b0ed8a2d74b80b4d909f1255473`.

## Configuración común preparada

Backend Transformers local, `trust_remote_code=false`, BF16 inicial, batch 1, contexto total 8192 tokens, temperatura 0, `do_sample=false`, semilla 0. Reservas de salida: 512 tokens para MC/semi_open y 1024 para open_ended. No se afirma que quepa en 24 GB. INT8/NF4 son fallbacks explícitos con registro previo de OOM BF16 compatible.

Se utiliza el chat template del snapshot. Qwen desactiva thinking expresamente; ALIA/Salamandra/Llama conservan sus templates nativos. Las restricciones de respuesta y la versión lógica del prompt son comunes. Los parámetros de generación se construyen de forma explícita, sin heredar distintas temperaturas/penalizaciones de las model cards.

La configuración pública consultada reporta 8192 posiciones para ALIA y 40960 para Qwen; se adopta el presupuesto común de 8192, sin activar extensiones de contexto. En modelos gated, la configuración real se comprueba al cargar el snapshot autorizado. Las afirmaciones de contexto de sus cards no sustituyen esa comprobación.

## Tamaño nominal frente a número de parámetros

La API oficial reportó 8.190.735.360 parámetros para Qwen3-8B y 8.030.261.248 para Llama 3.1-8B. ALIA y Salamandra: 7.768.117.248. Los dos nombres «8B» superan literalmente 8.000.000.000; se conserva su preparación porque son candidatos solicitados, pero **su elegibilidad competitiva bajo un límite numérico estricto requiere aclaración de la organización**. No se marca elegibilidad verificada ni se cambia el modelo silenciosamente.

Actualización 2026-10-01: el equipo decidió tratar Qwen3-8B como elegible porque el enunciado §3.1 lo sugiere textualmente. Los runners de GPU (`tools/run_b_gpu_4090.ps1`, `tools/kingscode_gpu_todo.ps1`) corren por defecto `qwen3-8b,alia-legal-7b`.

## Preparación reproducible y límites

`tools/prepare_models.py` descarga únicamente revisiones fijadas, verifica el SHA del repositorio y los hashes Git/LFS de todos los archivos necesarios, y guarda un manifest en `models/.kingscode_manifests/`. La ejecución posterior verifica hashes localmente y no contacta al Hub. Pesos y manifests de caché permanecen fuera de Git.

El registro de cada experimento conserva revisión, manifest de archivos, configuración, prompt, corpus/grafo, evidencia congelada y versiones de librerías. La compatibilidad del stack y los templates queda pendiente de ejecutar los tests y la prueba real en la GPU. No se han probado los modelos grandes en esta entrega.

Referencias de implementación: [descargas del Hub](https://huggingface.co/docs/huggingface_hub/guides/download), [generación Transformers](https://huggingface.co/docs/transformers/main/en/main_classes/text_generation), [cuantización opcional](https://huggingface.co/docs/transformers/quantization/bitsandbytes).
