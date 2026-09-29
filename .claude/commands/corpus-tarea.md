---
description: Ejecutar una tarea del plan de corpus v0.2 sin dañar ni inventar (uso: /corpus-tarea C1)
argument-hint: C0..C8
---
Tarea: $ARGUMENTS de docs/CORPUS_V02_PLAN.md.

1. Lee CLAUDE.md y docs/CORPUS_V02_PLAN.md completo (en especial la sección 3: no dañar / no alucinar).
2. Lee todos los archivos que la tarea toca y los reportes que cita. Verifica en el código que el diagnóstico sigue vigente; si cambió, dilo antes de seguir.
3. Escribe el plan: archivos, funciones, tests, datos de entrada, cómo se mide y criterio de aceptación. Espera mi aprobación.
4. Trabaja en una rama nueva. No toques corpus/, corpus_manifest.json, archivos oficiales ni código de B salvo lo que la tarea diga.
5. Todo dato jurídico sale de bytes oficiales descargados y verificados; si no se puede verificar, va al backlog. Ninguna pregunta, respuesta, resumen o metadato lo genera un modelo.
6. Corre la suite completa y la medición indicada. Reporta solo números de archivos generados en esta sesión, con su ruta; lo no ejecutado se reporta como no ejecutado.
7. Actualiza docs/DECISION_LOG.md y docs/KINGSCODE_STATE.json si corresponde, y deja el siguiente comando exacto.
