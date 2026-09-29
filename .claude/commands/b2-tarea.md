---
description: Ejecutar una tarea de B post-GPU (uso: /b2-tarea B7)
argument-hint: B0..B8
---
Tarea: $ARGUMENTS de docs/B_PLAN_POST_GPU.md.

1. Lee CLAUDE.md, docs/B_PLAN_POST_GPU.md completo (en especial las secciones 1 y 2) y los archivos que la tarea toca.
2. Verifica en el código que el estado descrito sigue vigente (rama base, funciones, archivos). Si no, dilo antes de seguir.
3. Escribe el plan: archivos, funciones, tests, cómo se mide y criterio de aceptación. Espera mi aprobación.
4. Rama nueva desde main actualizado. No toques código de A ni archivos oficiales. Cambios en legal.py/guards.py solo aditivos y con entrada en DECISION_LOG marcada "requiere revisión de Luis".
5. Ninguna respuesta, ejemplo ni dato lo genera un modelo cerrado; los tests usan fixtures oficiales o decoders falsos.
6. Corre la suite completa y la medición de la tarea. Reporta solo números de archivos generados en esta sesión, con ruta; lo no ejecutado, como no ejecutado.
7. Actualiza docs/KINGSCODE_STATE.json (member_b) y DECISION_LOG si corresponde, y deja el siguiente comando exacto.
