# Prototipo de B (referencia, no importar)

Código escrito fuera de este repo el 27-sep para la capa B, probado con backend mock y con un servidor
OpenAI-compatible falso: 50/50 filas válidas y 0 citas sin respaldo en el evaluador oficial.
Se deja aquí para portar ideas a `kingscode/reasoning/`, no para ejecutarlo desde este árbol
(sus imports apuntan a su paquete original `b.*`).

| Archivo | Qué portar |
|---|---|
| `prompts.py` | system prompt, pistas por `sub_tarea`, JSON schema por formato |
| `llm.py` | cliente `/v1/chat/completions` con JSON guiado, reintento y `enable_thinking=False` |
| `citerender.py` | tupla canónica de `citations.py` → texto que el extractor reconoce igual |
| `guard.py` | guarda que suprime oraciones con citas sin respaldo; `build_refs` |
| `answer.py` | armado de filas por formato con respaldos deterministas |
| `query.py` | correcciones de digitación y expansión controlada |
| `interfaz_app.py` | interfaz Streamlit mínima (respuesta + evidencia + JSON) |
