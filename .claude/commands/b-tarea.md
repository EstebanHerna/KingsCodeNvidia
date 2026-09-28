---
description: Ejecutar una tarea del plan de B con razonamiento primero (uso: /b-tarea T1)
argument-hint: T1..T7
---
Tarea: $ARGUMENTS de docs/B_EXTENSION_PLAN.md.

1. Lee CLAUDE.md y la sección de la tarea. Lee todos los archivos que toca.
2. Antes de editar, escribe: objetivo, archivos, diseño, riesgos, cómo lo vas a medir y criterio de aceptación. Espera mi aprobación.
3. Implementa con cambios mínimos y tests.
4. Corre la suite (`python -m unittest discover -s tests -v`) y la corrida de la muestra que corresponda.
5. Reporta tabla antes/después con el evaluador oficial, sin `--ragas` salvo que yo lo pida.
6. Actualiza docs/KINGSCODE_STATE.json y docs/DECISION_LOG.md si hubo decisión, y deja el siguiente comando exacto.
Respeta las reglas duras de CLAUDE.md, en especial: ninguna salida del sistema pasa por un modelo cerrado y nada con respuestas esperadas entra al pipeline.
