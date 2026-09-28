# Gate 1B — entrega y verificación

Estado: implementado y verificado dos veces, con retrieval real de A y backend dummy. La implementación de A, sus artefactos y los archivos oficiales se mantienen intactos. Este gate valida la integración pre-GPU; no constituye una entrega competitiva ni demuestra razonamiento jurídico.

## Archivos añadidos

- `kingscode/reasoning/__init__.py`: exportación de las interfaces públicas de B.
- `kingscode/reasoning/contracts.py`: preguntas tipadas y proyección exclusiva de campos públicos.
- `kingscode/reasoning/legal.py`: reconocimiento de referencias y compatibilidad de identidad primaria/año/artículo.
- `kingscode/reasoning/query.py`: normalización conservadora y expansiones finitas.
- `kingscode/reasoning/routing.py`: OFF/AUTO/ON y adaptador booleano inyectable en A.
- `kingscode/reasoning/policy.py`: abstención ante evidencia insuficiente o conflictos fuertes.
- `kingscode/reasoning/decoder.py`: contrato de decoder, prompts por formato y dummy determinista.
- `kingscode/reasoning/guards.py`: validación estricta y citation guard con trazabilidad.
- `kingscode/reasoning/pipeline.py`: coordinación mediante la API pública de retrieval.
- `kingscode/reasoning/evaluation.py`: ejecución del evaluador oficial intacto, sin RAGAS.
- `kingscode/reasoning/experiments.py`: registro de configuraciones, hashes, métricas, trazas y fallos.
- `config/reasoning.json`, `tools/member_b.py`: configuración y comando único offline.
- `tests/test_reasoning.py`, `tests/fixtures/member_b_official_passages.json`: 44 pruebas nuevas con cinco pasajes literales del corpus oficial; los casos negativos modificados solo ejercitan las guardas.
- `tools/verify_member_b_second.py`: auditoría independiente y reproducción en otro proceso.
- `docs/MEMBER_B_RUNBOOK.md`: interfaces, comandos, decisiones y límites.
- `reports/member_b/*/{questions.jsonl,submissions.jsonl,trace.jsonl,evaluation.json,experiment.json}`: historial de tres corridas, sin editar resultados finales. La última corrida es la referencia de esta entrega.
- `reports/member_b_second_verification.json`, `reports/member_b_tests_second.txt` y este informe.

## Documentación/configuración actualizada

`README.md`, `README_KINGSCODE.md`, `START_HERE.md`, `config/strategy.json`, `docs/KINGSCODE_STATE.json`, `docs/KINGSCODE_MASTER_KNOWLEDGE.md`, `docs/DECISION_LOG.md`, `docs/INTEGRATION_CONTRACTS.md`, `docs/MEMBER_B_REASONING_EVAL_PLAN.md`, `docs/ROADMAP.md` y `docs/VERIFICATION.md` reflejan lo implementado y conservan CUDA/bakeoff como pendientes.

## Pruebas y resultado

1. `.venv/Scripts/python.exe -m unittest discover -s tests -v`: 60/60 pruebas aprobadas (44 de B + 16 previas), sin fallos ni saltos; 18,173 s en el primer pase final.
2. `.venv/Scripts/python.exe tools/member_b.py smoke`: 50/50 filas válidas, 50 abstenciones del dummy; OFF 40 / AUTO 6 / ON 4. Cero citas emitidas, por lo que la tasa de citas sin respaldo cero no mide calidad. El evaluador oficial reportó cero errores y 5/50 puntos sin RAGAS.
3. `.venv/Scripts/python.exe tools/verify_member_b_second.py`: segunda suite 60/60 en 17,217 s; 19 archivos oficiales intactos; 15 archivos de A idénticos al commit original; corpus, grafo e índice sin cambios; 400 evidencias cotejadas literalmente con el corpus. Nueva ejecución en otro proceso con JSONL idéntico byte a byte, mismas decisiones/trazas sin tiempos y mismo resultado oficial. Ningún módulo neuronal cargado.

Corrida final: [experiment.json](member_b/20260928T035443616407Z-9a776fef5883/experiment.json). Fingerprint `9a776fef5883eb012f875170e6942ac2ed1aeb7621fabc322f3fb24201c849e9`. SHA-256 del JSONL `09d9ac32ac981162105d91fc127dedd770023e6b5ca122d8cedfca5190f4767a`.

## Decisiones y límites pendientes

- El schema oficial describe `null` para opción múltiple con abstención, pero su enum efectivo lo rechaza. Se conserva intacto: el dummy emite abstención true y A como marcador formal, explicando expresamente que no representa una elección. No consulta la opción esperada.
- La guarda certifica identidad normativa/artículo y procedencia, no implicación semántica general. Rangos textuales, referencias implícitas y casos de citación complejos quedan sujetos a abstención/revisión.
- Las reglas de routing y suficiencia son conservadoras; todavía falta calibrarlas con un decoder real. No hay GPU, decoder real, bakeoff, RAGAS ni benchmark neuronal completo en este gate.
- Continúan el backlog de adquisición/ambigüedad de A, la revisión de vigencia y el freeze competitivo. No se rehizo esa capa.

## Siguiente comando exacto

Desde la raíz, con el entorno y snapshot local de A disponibles:

```powershell
.venv/Scripts/python.exe tools/member_b.py smoke
```

Después, revisar las trazas y repetir `tools/verify_member_b_second.py` antes de una tarea separada de integración de decoder/GPU. Para un clon nuevo, seguir el runbook de A para disponer del corpus; descargar otra vez fuentes públicas puede cambiar sus hashes.
