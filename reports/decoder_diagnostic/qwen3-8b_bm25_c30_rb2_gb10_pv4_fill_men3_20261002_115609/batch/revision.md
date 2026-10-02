# Revisión por pregunta

## 24 · semi_open

**Pregunta:** ¿Cuáles son los elementos esenciales de validez de un contrato?

**Medición:** cita=sin_ref_parseable · legal_basis=None

**Respuesta final:**
```json
{
  "respuesta": "Los elementos esenciales de validez de un contrato incluyen el consentimiento libre y espontáneo de los contrayentes, la capacidad de las partes y el cumplimiento de las formalidades legales. Estos elementos son fundamentales para que un contrato tenga efectos jurídicos, según lo establecido en la doctrina y aplicado en el derecho colombiano.",
  "palabras_clave": [
    "elementos esenciales",
    "validez",
    "contrato",
    "derecho colombiano"
  ],
  "referencia_legal": "Sentencia SU-214 de 2016; artículo 1045 del Código de Comercio; artículo 1 de la Ley 50 de 1990; artículo 1501 del Código Civil; artículo 23 del Código Sustantivo del Trabajo; Constitución Política; Sentencia C-577 de 2011; Sentencia C-397 de 2006"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "Los elementos esenciales de validez de un contrato incluyen el consentimiento libre y espontáneo de los contrayentes, la capacidad de las partes y el cumplimiento de las formalidades legales. Estos elementos son fundamentales para que un contrato tenga efectos jurídicos, según lo establecido en la doctrina y aplicado en el derecho colombiano.",
  "palabras_clave": ["elementos esenciales", "validez", "contrato", "derecho colombiano"],
  "referencia_legal": "Sentencia SU-214 de 2016",
  "pasajes_usados": [
    "sentencia_su_214_de_2016:00248:1284d90b7401",
    "sentencia_su_214_de_2016:00240:6d3bf6eb0ccc"
  ]
}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 1 → después 12 · reparación {} · construidas ['Sentencia SU-214 de 2016', 'artículo 1045 del Código de Comercio', 'artículo 1 de la Ley 50 de 1990', 'artículo 1501 del Código Civil', 'artículo 23 del Código Sustantivo del Trabajo', 'Constitución Política', 'Sentencia C-577 de 2011', 'Sentencia C-397 de 2006']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00248:1284d90b7401', 'sentencia_su_214_de_2016:00240:6d3bf6eb0ccc']
**Evidencia:**
1. `sentencia_su_214_de_2016:00248:1284d90b7401` — Sentencia SU-214 de 2016 art. None
2. `codigo_comercio:01106:f65f7780a57d` — Código de Comercio (Decreto 410 de 1971) art. 1045
3. `sentencia_su_214_de_2016:00214:e6da86aa9dec` — Sentencia SU-214 de 2016 art. None
4. `ley_50_de_1990:00000:72aa613d77a5` — Ley 50 de 1990 art. 1
5. `sentencia_su_214_de_2016:00240:6d3bf6eb0ccc` — Sentencia SU-214 de 2016 art. None
6. `codigo_civil:01499:977520c226b2` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1501
7. `codigo_sustantivo_trabajo:00022:d44874b99a5a` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 23
8. `sentencia_c_134_de_2019:00015:f9b6a445d894` — Sentencia C-134 de 2019 art. None
*Tokens 6246→220 · generación 9321.16859999951 ms · retrieval 7.8092999901855364 ms · grafo off*

## 51 · multiple_choice · ✔ correcta

**Pregunta:** ¿En cuál de los siguientes casos procede la acción judicial de grupo? 

- A: Cuando un grupo de personas busca proteger derechos fundamentales individuales de aplicación inmediata.
- B: Cuando un grupo de ciudadanos busca defender el interés colectivo ambiental o del espacio público.
- C: Cuando un conjunto de personas resulta afectado por un mismo hecho que les causa perjuicios individuales derivados de una causa común.
- D: Cuando se pretende declarar la inconstitucionalidad de una norma con fuerza de ley.

**Medición:** cita=cita_ok · legal_basis=Constitución Política, artículo 88; Ley 472 de 1998, artículos 3 y 46.

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "La acción de grupo se define como un mecanismo judicial que permite a un grupo de personas actuar conjuntamente para defender derechos fundamentales que les son comunes, siempre que se encuentren en condiciones similares y la vulneración de esos derechos afecte a todos ellos. En la Sentencia SU-429 de 2024, se menciona que la acción de grupo se aplica cuando se persigue el reconocimiento y pago de un daño atribuible al Estado por su participación en un crimen de lesa humanidad, y se establece que la caducidad de la acción de grupo se aplica a partir de la fecha en que se incoa la acción. Además, se afirma que la acción de grupo se aplica cuando se busca la protección de derechos fundamentales que afectan a un grupo de personas, y que la Corte Constitucional ha sostenido que la acción de tutela puede proceder contra providencias judiciales cuando no existen otros medios de defensa judicial. En este contexto, la opción C se alinea con la definición de la acción de grupo, ya que se refiere a un conjunto de personas afectadas por un mismo hecho que les causa perjuicios individuales derivados de una causa común. Las opciones A, B y D no se ajustan a la definición de la acción de grupo tal como se establece en los pasajes proporcionados. Fundamento normativo: Sentencia SU-455 de 2020; Sentencia SU-214 de 2016; Sentencia C-259 de 2015; artículo 54 del Código Nacional de Seguridad y Convivencia Ciudadana; Ley 472 de 1998; Código de Procedimiento Administrativo y de lo Contencioso Administrativo; Constitución Política.",
  "descarte_opciones": {
    "A": "La opción A se refiere a la protección de derechos fundamentales individuales de aplicación inmediata, lo cual no se ajusta a la definición de la acción de grupo, que se aplica a un grupo de personas afectadas por un mismo hecho.",
    "B": "La opción B se refiere a la defensa del interés colectivo ambiental o del espacio público, lo cual no se ajusta a la definición de la acción de grupo, que se aplica a un grupo de personas afectadas por un mismo hecho.",
    "D": "La opción D se refiere a la declaración de inconstitucionalidad de una norma con fuerza de ley, lo cual no se ajusta a la definición de la acción de grupo, que se aplica a un grupo de personas afectadas por un mismo hecho."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "La acción de grupo se define como un mecanismo judicial que permite a un grupo de personas actuar conjuntamente para defender derechos fundamentales que les son comunes, siempre que se encuentren en condiciones similares y la vulneración de esos derechos afecte a todos ellos. En la Sentencia SU-429 de 2024, se menciona que la acción de grupo se aplica cuando se persigue el reconocimiento y pago de un daño atribuible al Estado por su participación en un crimen de lesa humanidad, y se establece que la caducidad de la acción de grupo se aplica a partir de la fecha en que se incoa la acción. Además, se afirma que la acción de grupo se aplica cuando se busca la protección de derechos fundamentales que afectan a un grupo de personas, y que la Corte Constitucional ha sostenido que la acción de tutela puede proceder contra providencias judiciales cuando no existen otros medios de defensa judicial. En este contexto, la opción C se alinea con la definición de la acción de grupo, ya que se refiere a un conjunto de personas afectadas por un mismo hecho que les causa perjuicios individuales derivados de una causa común. Las opciones A, B y D no se ajustan a la definición de la acción de grupo tal como se establece en los pasajes proporcionados.",
  "respuesta_correcta": "C",
  "descarte_opciones": {
    "A": "La opción A se refiere a la protección de derechos fundamentales individuales de aplicación inmediata, lo cual no se ajusta a la definición de la acción de grupo, que se aplica a un grupo de personas afectadas por un mismo hecho.",
    "B": "La opción B se refiere a la defensa del interés colectivo ambiental o del espacio público, lo cual no se ajusta a la definición de la acción de grupo, que se aplica a un grupo de personas afectadas por un mismo hecho.",
    "D": "La opción D se refiere a la declaración de inconstitucionalidad de una norma con fuerza de ley, lo cual no se ajusta a la definición de la acción de grupo, que se aplica a un grupo de personas afectadas por un mismo hecho."
  },
  "pasajes_usados": [
    "sentencia_su_429_de_2024:00022:7edfe1f0dc75",
    "sentencia_su_429_de_2024:00037:107e51e4d8bb",
    "sentencia_su_429_de_2024:00061:860f569e5e39",
    "sentencia_su_455_de_2020:00015:26ded4ad04e0"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 9 · reparación {} · construidas ['Sentencia SU-429 de 2024', 'Sentencia SU-455 de 2020', 'Sentencia SU-214 de 2016', 'Sentencia C-259 de 2015', 'artículo 54 del Código Nacional de Seguridad y Convivencia Ciudadana', 'Ley 472 de 1998', 'Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_su_429_de_2024:00022:7edfe1f0dc75', 'sentencia_su_429_de_2024:00037:107e51e4d8bb', 'sentencia_su_429_de_2024:00061:860f569e5e39', 'sentencia_su_455_de_2020:00015:26ded4ad04e0']
**Evidencia:**
1. `sentencia_su_214_de_2016:00237:d3bc4e76d291` — Sentencia SU-214 de 2016 art. None
2. `sentencia_su_429_de_2024:00022:7edfe1f0dc75` — Sentencia SU-429 de 2024 art. None
3. `sentencia_su_429_de_2024:00037:107e51e4d8bb` — Sentencia SU-429 de 2024 art. None
4. `sentencia_su_429_de_2024:00061:860f569e5e39` — Sentencia SU-429 de 2024 art. None
5. `sentencia_su_455_de_2020:00015:26ded4ad04e0` — Sentencia SU-455 de 2020 art. None
6. `sentencia_c_259_de_2015:00009:1a0174281fcf` — Sentencia C-259 de 2015 art. None
7. `sentencia_su_429_de_2024:00001:c6f8eb4a737f` — Sentencia SU-429 de 2024 art. None
8. `codigo_nacional_policia:00054:9aed0cdab1f8` — Código Nacional de Seguridad y Convivencia Ciudadana (Ley 1801 de 2016) art. 54
*Tokens 6805→658 · generación 29917.444399994565 ms · retrieval 75.57709999673534 ms · grafo off*

## 58 · multiple_choice · ✘ esperada A

**Pregunta:** ¿Qué normativa regula las actuaciones jurisdiccionales adelantadas ante la SIC?

- A: Ley 1564 de 2002
- B: Ley 270 de 1996
- C: Ley 472 de 1998
- D: Ley 906 de 2004

**Medición:** cita=cita_ok · legal_basis=Ley 1564 de 2002 (El Estatuto del Consumidor). 

**Respuesta final:**
```json
{
  "respuesta_correcta": "D",
  "justificacion": "La pregunta se refiere a la normativa que regula las actuaciones jurisdiccionales adelantadas ante la SIC. Además, se menciona que las superintendencias, incluida la SIC, ejercen funciones de vigilancia y control, y en algunos casos, funciones jurisdiccionales en determinados ámbitos definidos en la ley. Sin embargo, no se menciona directamente una norma específica que regule las actuaciones jurisdiccionales ante la SIC. Por lo tanto, no se puede determinar con base en la evidencia proporcionada. Fundamento normativo: Sentencia C-748 de 2011; artículo 1 del Código General del Proceso; Sentencia T-232 de 2025; artículo 153 del Código de la Infancia y la Adolescencia; Sentencia SU-429 de 2024; Sentencia C-1011 de 2008; Decreto 2153 de 1992; Constitución Política.",
  "descarte_opciones": {
    "A": "La no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.",
    "B": "La no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.",
    "C": "La no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La pregunta se refiere a la normativa que regula las actuaciones jurisdiccionales adelantadas ante la SIC. En la evidencia, se menciona que la SIC es un organismo de carácter técnico adscrito al Ministerio de Desarrollo Económico, según el artículo 1° del Decreto 2153 de 1992. Además, se menciona que las superintendencias, incluida la SIC, ejercen funciones de vigilancia y control, y en algunos casos, funciones jurisdiccionales en determinados ámbitos definidos en la ley. Sin embargo, no se menciona directamente una norma específica que regule las actuaciones jurisdiccionales ante la SIC. Por lo tanto, no se puede determinar con base en la evidencia proporcionada.","respuesta_correcta":"D","descarte_opciones":{"A":"La Ley 1564 de 2002 no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.","B":"La Ley 270 de 1996 no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC.","C":"La Ley 472 de 1998 no se menciona en la evidencia como normativa que regule las actuaciones jurisdiccionales ante la SIC."},"pasajes_usados":["sentencia_c_748_de_2011:00226:c8d13ad22037"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 10 · reparación {'suppressed_fragment': 3, 'suppressed_sentence': 4} · construidas ['Sentencia C-748 de 2011', 'artículo 1 del Código General del Proceso', 'Sentencia T-232 de 2025', 'artículo 153 del Código de la Infancia y la Adolescencia', 'Sentencia SU-429 de 2024', 'Sentencia C-1011 de 2008', 'Decreto 2153 de 1992', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_c_748_de_2011:00226:c8d13ad22037']
**Evidencia:**
1. `codigo_general_proceso:00000:7e5b524b91ca` — Código General del Proceso (Ley 1564 de 2012) art. 1
2. `sentencia_t_232_de_2025:00013:9facb594dde9` — Sentencia T-232 de 2025 art. None
3. `sentencia_c_748_de_2011:00226:c8d13ad22037` — Sentencia C-748 de 2011 art. None
4. `codigo_infancia:00160:32878d3155d7` — Código de la Infancia y la Adolescencia (Ley 1098 de 2006) art. 153
5. `sentencia_su_429_de_2024:00050:11c63eee45e9` — Sentencia SU-429 de 2024 art. None
6. `codigo_general_proceso:00279:ce2c4c6e91fd` — Código General del Proceso (Ley 1564 de 2012) art. 275
7. `codigo_disciplinario:00154:59d343ebe57f` — Código General Disciplinario (Ley 1952 de 2019) art. 153
8. `codigo_procedimiento_penal:00023:01eff21653ac` — Código de Procedimiento Penal (Ley 906 de 2004) art. 24
*Tokens 4733→363 · generación 14275.964899992687 ms · retrieval 205.1429000130156 ms · grafo off*

## 60 · multiple_choice · ✔ correcta

**Pregunta:** ¿Cuál de las siguientes afirmaciones refleja correctamente el principio del juez natural en el proceso judicial colombiano?

- A: Nadie puede ser juzgado sino por un juez o tribunal competente, previamente establecido por la ley.
- B: El juez natural es aquel designado discrecionalmente por el Consejo Superior de la Judicatura.
- C: El principio del juez natural se refiere únicamente a la imparcialidad del funcionario, no a su competencia.
- D: Toda persona puede ser juzgada por cualquier autoridad que tenga competencia general sobre el asunto.

**Medición:** cita=cita_ok · legal_basis=Constitución Política de Colombia, artículo 29; Código General del Proceso (Ley 1564 de 2012), artículo 6.

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "Además, se menciona que la garantía del juez natural es un elemento constitutivo del derecho al debido proceso y que el juez natural debe ser un humano, no una máquina. Por otro lado, la Sentencia SU-500 de 2015 afirma que el juez natural no puede ser desplazado por el juez constitucional, lo que reafirma la importancia de la competencia del juez natural. La opción A refleja correctamente esta idea, ya que establece que nadie puede ser juzgado sino por un juez o tribunal competente, previamente establecido por la ley. Las opciones B, C y D no se alinean con los principios establecidos en las sentencias mencionadas. Fundamento normativo: Sentencia T-323 de 2024; Sentencia SU-16 de 2020; artículo 48 del Código General del Proceso; artículo 328 de la Ley 2452 de 2025; Constitución Política; Ley 270 de 1996; Ley 74 de 1968.",
  "descarte_opciones": {
    "B": "La opción B no se menciona en la evidencia y contradice la idea de que el juez natural debe ser establecido por la ley.",
    "C": "La opción C es incorrecta porque el principio del juez natural no se refiere únicamente a la imparcialidad, sino también a la competencia.",
    "D": "La opción D es incorrecta porque no se menciona que cualquier autoridad con competencia general pueda juzgar a una persona."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "La Sentencia T-323 de 2024 establece que el juez natural es aquel a quien la Constitución o la ley le ha atribuido el conocimiento de determinado asunto. Además, se menciona que la garantía del juez natural es un elemento constitutivo del derecho al debido proceso y que el juez natural debe ser un humano, no una máquina. Por otro lado, la Sentencia SU-500 de 2015 afirma que el juez natural no puede ser desplazado por el juez constitucional, lo que reafirma la importancia de la competencia del juez natural. La opción A refleja correctamente esta idea, ya que establece que nadie puede ser juzgado sino por un juez o tribunal competente, previamente establecido por la ley. Las opciones B, C y D no se alinean con los principios establecidos en las sentencias mencionadas.",
  "respuesta_correcta": "A",
  "descarte_opciones": {
    "B": "La opción B no se menciona en la evidencia y contradice la idea de que el juez natural debe ser establecido por la ley.",
    "C": "La opción C es incorrecta porque el principio del juez natural no se refiere únicamente a la imparcialidad, sino también a la competencia.",
    "D": "La opción D es incorrecta porque no se menciona que cualquier autoridad con competencia general pueda juzgar a una persona."
  },
  "pasajes_usados": [
    "sentencia_t_323_de_2024:00054:ac1fc23534b8",
    "sentencia_t_323_de_2024:00055:b6b938c746e1",
    "sentencia_t_323_de_2024:00057:ed6ca92308cc",
    "sentencia_t_323_de_2024:00056:bb28fe8afde4",
    "sentencia_su_500_de_2015:00030:1a0700efdc3e"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 10 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia T-323 de 2024', 'Sentencia SU-500 de 2015', 'Sentencia SU-16 de 2020', 'artículo 48 del Código General del Proceso', 'artículo 328 de la Ley 2452 de 2025', 'Constitución Política', 'Ley 270 de 1996', 'Ley 74 de 1968']
**Pasajes declarados por el modelo:** ['sentencia_t_323_de_2024:00054:ac1fc23534b8', 'sentencia_t_323_de_2024:00055:b6b938c746e1', 'sentencia_t_323_de_2024:00057:ed6ca92308cc', 'sentencia_t_323_de_2024:00056:bb28fe8afde4', 'sentencia_su_500_de_2015:00030:1a0700efdc3e']
**Evidencia:**
1. `sentencia_t_323_de_2024:00054:ac1fc23534b8` — Sentencia T-323 de 2024 art. None
2. `sentencia_t_323_de_2024:00055:b6b938c746e1` — Sentencia T-323 de 2024 art. None
3. `sentencia_t_323_de_2024:00057:ed6ca92308cc` — Sentencia T-323 de 2024 art. None
4. `sentencia_su_16_de_2020:00151:7e8f2da0f8cd` — Sentencia SU-16 de 2020 art. None
5. `sentencia_t_323_de_2024:00056:bb28fe8afde4` — Sentencia T-323 de 2024 art. None
6. `sentencia_su_500_de_2015:00030:1a0700efdc3e` — Sentencia SU-500 de 2015 art. None
7. `codigo_general_proceso:00050:94645e1b54fd` — Código General del Proceso (Ley 1564 de 2012) art. 48
8. `ley_2452_de_2025:00335:4f7ac5deff87` — Ley 2452 de 2025 art. 328
*Tokens 6555→523 · generación 21668.468500007293 ms · retrieval 83.89110000280198 ms · grafo off*

## 79 · semi_open

**Pregunta:** ¿Existe alguna norma en el ordenamiento jurídico colombiano que regule el acoso laboral?

**Medición:** cita=cita_ok · legal_basis=Ley 1010 de 2006 

**Respuesta final:**
```json
{
  "respuesta": "Sí, existe normativa en el ordenamiento jurídico colombiano que regula el acoso laboral. La Ley 1010 de 2006 establece medidas preventivas y correctivas para el acoso laboral, entre ellas, la creación de mecanismos internos de conciliación y la obligación de los empleadores de adoptar procedimientos confidenciales y efectivos para resolver las quejas. Además, la Sentencia T-262 de 2025 reafirma la importancia de estas normas en la protección del derecho al debido proceso de las víctimas de acoso laboral.",
  "palabras_clave": [
    "acoso laboral",
    "Ley 1010 de 2006",
    "derecho al debido proceso"
  ],
  "referencia_legal": "artículo 9 de la Ley 1010 de 2006; Sentencia T-262 de 2025; artículo 6 de la Ley 1010 de 2006; Sentencia T-317 de 2020; Sentencia C-960 de 2007; Código Sustantivo del Trabajo"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"Sí, existe normativa en el ordenamiento jurídico colombiano que regula el acoso laboral. La Ley 1010 de 2006 establece medidas preventivas y correctivas para el acoso laboral, entre ellas, la creación de mecanismos internos de conciliación y la obligación de los empleadores de adoptar procedimientos confidenciales y efectivos para resolver las quejas. Además, la Sentencia T-262 de 2025 reafirma la importancia de estas normas en la protección del derecho al debido proceso de las víctimas de acoso laboral.","palabras_clave":["acoso laboral","Ley 1010 de 2006","derecho al debido proceso"],"referencia_legal":"Ley 1010 de 2006, artículo 9; Sentencia T-262 de 2025","pasajes_usados":["ley_1010_de_2006:00008:9146ba17697d","sentencia_t_262_de_2025:00027:471c090a71fe"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 6 → después 11 · reparación {'rewritten_to_body': 1} · construidas ['artículo 9 de la Ley 1010 de 2006', 'Sentencia T-262 de 2025', 'artículo 6 de la Ley 1010 de 2006', 'Sentencia T-317 de 2020', 'Sentencia C-960 de 2007', 'Código Sustantivo del Trabajo']
**Pasajes declarados por el modelo:** ['ley_1010_de_2006:00008:9146ba17697d', 'sentencia_t_262_de_2025:00027:471c090a71fe']
**Evidencia:**
1. `sentencia_t_262_de_2025:00040:e09f9f29a4ca` — Sentencia T-262 de 2025 art. None
2. `sentencia_t_262_de_2025:00032:50ae27ba74c6` — Sentencia T-262 de 2025 art. None
3. `sentencia_t_262_de_2025:00027:471c090a71fe` — Sentencia T-262 de 2025 art. None
4. `ley_1010_de_2006:00008:9146ba17697d` — Ley 1010 de 2006 art. 9
5. `sentencia_t_262_de_2025:00024:716775f740fc` — Sentencia T-262 de 2025 art. None
6. `sentencia_t_262_de_2025:00000:1c33f1d0e919` — Sentencia T-262 de 2025 art. None
7. `ley_1010_de_2006:00005:68b3af1ab339` — Ley 1010 de 2006 art. 6
8. `sentencia_t_262_de_2025:00037:fb5768aca244` — Sentencia T-262 de 2025 art. None
*Tokens 6945→283 · generación 12144.590900003095 ms · retrieval 9.972400002880022 ms · grafo off*

## 128 · multiple_choice · ✘ esperada D

**Pregunta:** ¿Quiénes tienen la facultad de otorgar contratos de leasing financiero o arrendamiento financiero en Colombia? 

- A: Compañías de Financiamiento, los Bancos Comerciales, Fintech, Cooperativas, Fundaciones y Asociaciones
- B: Compañías de Financiamiento y Bancos Comerciales
- C: Cooperativas, Fundaciones y Asociaciones
- D: Compañías de Financiamiento, los Bancos Comerciales y las Fintech

**Medición:** cita=cita_ok · legal_basis=Decreto Ley 663 de 1993

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "La norma que establece quiénes pueden otorgar contratos de leasing financiero o arrendamiento financiero en Colombia se encuentra en el Decreto 663 de 1993, artículo 141. Según este artículo, las compañías de financiamiento comercial pueden realizar operaciones de leasing desde el 1 de julio de 1993, hasta el porcentaje máximo que señale el Gobierno Nacional. Además, el artículo 26 del mismo Decreto 663 de 1993 establece que las compañías de financiamiento comercial pueden recibir créditos para la adquisición de activos objeto de operaciones de leasing. Por lo tanto, las compañías de financiamiento comercial son las que tienen la facultad de otorgar contratos de leasing financiero o arrendamiento financiero en Colombia. Fundamento normativo: artículo 76 de la Ley 1819 de 2016; artículo 127-1 del Estatuto Tributario; Ley 510 de 1999; Constitución Política; Decreto 2816 de 1991.",
  "descarte_opciones": {
    "A": "No se menciona que las Fintech, Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.",
    "C": "No se menciona que las Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.",
    "D": "No se menciona que las Fintech tengan esta facultad en la norma."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La norma que establece quiénes pueden otorgar contratos de leasing financiero o arrendamiento financiero en Colombia se encuentra en el Decreto 663 de 1993, artículo 141. Según este artículo, las compañías de financiamiento comercial pueden realizar operaciones de leasing desde el 1 de julio de 1993, hasta el porcentaje máximo que señale el Gobierno Nacional. Además, el artículo 26 del mismo Decreto 663 de 1993 establece que las compañías de financiamiento comercial pueden recibir créditos para la adquisición de activos objeto de operaciones de leasing. Por lo tanto, las compañías de financiamiento comercial son las que tienen la facultad de otorgar contratos de leasing financiero o arrendamiento financiero en Colombia.","respuesta_correcta":"B","descarte_opciones":{"A":"No se menciona que las Fintech, Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.","C":"No se menciona que las Cooperativas, Fundaciones y Asociaciones tengan esta facultad en la norma.","D":"No se menciona que las Fintech tengan esta facultad en la norma."},"pasajes_usados":["decreto_663_de_1993:00204:4acf56878fce","decreto_663_de_1993:00035:8c6a5f6a33f5"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 11 · reparación {} · construidas ['artículo 141 del Decreto 663 de 1993', 'artículo 26 del Decreto 663 de 1993', 'artículo 76 de la Ley 1819 de 2016', 'artículo 127-1 del Estatuto Tributario', 'artículo 142 del Decreto 663 de 1993', 'Ley 510 de 1999', 'Constitución Política', 'Decreto 2816 de 1991']
**Pasajes declarados por el modelo:** ['decreto_663_de_1993:00204:4acf56878fce', 'decreto_663_de_1993:00035:8c6a5f6a33f5']
**Evidencia:**
1. `ley_1819_de_2016:00088:f41467d4481e` — Ley 1819 de 2016 art. 76
2. `decreto_663_de_1993:00204:4acf56878fce` — Decreto 663 de 1993 art. 141
3. `estatuto_tributario:00224:0fea97482b61` — Estatuto Tributario (Decreto 624 de 1989) art. 127-1
4. `decreto_663_de_1993:00205:90c1f38b0893` — Decreto 663 de 1993 art. 142
5. `estatuto_tributario:00441:2506b7a4f0cb` — Estatuto Tributario (Decreto 624 de 1989) art. 267-1
6. `ley_1819_de_2016:00143:93d0590730a1` — Ley 1819 de 2016 art. 115
7. `decreto_663_de_1993:00035:8c6a5f6a33f5` — Decreto 663 de 1993 art. 26
8. `estatuto_tributario:00225:bf4fe5bcaf05` — Estatuto Tributario (Decreto 624 de 1989) art. 127-1
*Tokens 5532→353 · generación 13964.477300003637 ms · retrieval 31.782199992449023 ms · grafo off*

## 140 · semi_open

**Pregunta:** ¿Qué definió la Corte Constitucional en la Sentencia C 145 de 2018 frente a las potestades del acreedor garantizado que ejecuta la garantía mobiliaria fuera o dentro de un proceso concursal?

**Medición:** cita=cita_ok · legal_basis=Sentencia C 145 de 2018

**Respuesta final:**
```json
{
  "respuesta": "La Corte Constitucional definió en la Sentencia C-145 de 2018 que las potestades del acreedor garantizado para ejecutar la garantía mobiliaria fuera o dentro de un proceso concursal son exequibles condicionadas. Esto significa que solo proceden siempre que los demás bienes del deudor sean suficientes para asegurar el pago de las obligaciones alimentarias de los niños y las salariales y prestaciones derivadas del contrato de trabajo.",
  "palabras_clave": [
    "Corte Constitucional",
    "acreedor garantizado",
    "garantía mobiliaria",
    "derechos de los niños",
    "derechos de los trabajadores"
  ],
  "referencia_legal": "Sentencia C-145 de 2018; Ley 1676 de 2013; Código Civil; Constitución Política"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La Corte Constitucional definió en la Sentencia C-145 de 2018 que las potestades del acreedor garantizado para ejecutar la garantía mobiliaria fuera o dentro de un proceso concursal son exequibles condicionadas. Esto significa que solo proceden siempre que los demás bienes del deudor sean suficientes para asegurar el pago de las obligaciones alimentarias de los niños y las salariales y prestaciones derivadas del contrato de trabajo. La Corte reiteró que estas normas deben aplicarse bajo el marco del artículo 2498 del Código Civil, garantizando así la protección constitucional de los derechos de los niños y los trabajadores.","palabras_clave":["Corte Constitucional","acreedor garantizado","garantía mobiliaria","derechos de los niños","derechos de los trabajadores"],"referencia_legal":"Sentencia C-145 de 2018","pasajes_usados":["sentencia_c_145_de_2018:00035:4dfb7ce4e3b6","sentencia_c_145_de_2018:00034:544f29faa993"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 5 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia C-145 de 2018', 'Ley 1676 de 2013', 'Código Civil', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_c_145_de_2018:00035:4dfb7ce4e3b6', 'sentencia_c_145_de_2018:00034:544f29faa993']
**Evidencia:**
1. `sentencia_c_145_de_2018:00022:4b9680b22d10` — Sentencia C-145 de 2018 art. None
2. `sentencia_c_145_de_2018:00035:4dfb7ce4e3b6` — Sentencia C-145 de 2018 art. None
3. `sentencia_c_145_de_2018:00032:dad2883033e1` — Sentencia C-145 de 2018 art. None
4. `sentencia_c_145_de_2018:00034:544f29faa993` — Sentencia C-145 de 2018 art. None
5. `sentencia_c_145_de_2018:00007:65b81292b813` — Sentencia C-145 de 2018 art. None
6. `sentencia_c_145_de_2018:00033:4db06e328a80` — Sentencia C-145 de 2018 art. None
7. `sentencia_c_145_de_2018:00014:1c8c5f56a51c` — Sentencia C-145 de 2018 art. None
8. `sentencia_c_145_de_2018:00015:00317177d1ef` — Sentencia C-145 de 2018 art. None
*Tokens 7002→287 · generación 12641.418699990027 ms · retrieval 26.75529998668935 ms · grafo off*

## 142 · semi_open

**Pregunta:** ¿Cuál es el precedente jurisprudencial en materia de deducibilidad de gastos en el impuesto sobre la renta?

**Medición:** cita=sin_ref_parseable · legal_basis=Sentencia de unificación 2020CE-SUJ-4-005 del 26 de noviembre de 2020 con expediente 21329.

**Respuesta final:**
```json
{
  "respuesta": "En el derecho colombiano, no existe un precedente jurisprudencial específico mencionado en la evidencia proporcionada sobre la deducibilidad de gastos en el impuesto sobre la renta. La normativa relevante se encuentra en el Estatuto Tributario (Decreto 624 de 1989) y en la Ley 1819 de 2016, que establecen reglas sobre la deducibilidad de ciertos gastos y la no deducibilidad de otros. Estas normas son las que regulan directamente el tema.",
  "palabras_clave": [
    "deducibilidad",
    "gastos",
    "impuesto sobre la renta",
    "Estatuto Tributario",
    "Ley 1819 de 2016"
  ],
  "referencia_legal": "artículo 85 del Estatuto Tributario; artículo 59 de la Ley 1819 de 2016; artículo 61 de la Ley 1819 de 2016; artículo 32 de la Ley 1819 de 2016; artículo 33 del Estatuto Tributario; Ley 863 de 2003; Ley 223 de 1995; Ley 2010 de 2019"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"En el derecho colombiano, no existe un precedente jurisprudencial específico mencionado en la evidencia proporcionada sobre la deducibilidad de gastos en el impuesto sobre la renta. La normativa relevante se encuentra en el Estatuto Tributario (Decreto 624 de 1989) y en la Ley 1819 de 2016, que establecen reglas sobre la deducibilidad de ciertos gastos y la no deducibilidad de otros. Estas normas son las que regulan directamente el tema.","palabras_clave":["deducibilidad","gastos","impuesto sobre la renta","Estatuto Tributario","Ley 1819 de 2016"],"referencia_legal":"Estatuto Tributario (Decreto 624 de 1989), artículo 85; Ley 1819 de 2016, artículo 59; Ley 1819 de 2016, artículo 61; Ley 1819 de 2016, artículo 32; Estatuto Tributario (Decreto 624 de 1989), artículo 33","pasajes_usados":["estatuto_tributario:00139:1d45173d5fa5","ley_1819_de_2016:00069:806b08149137","ley_1819_de_2016:00071:5a746eec5119","ley_1819_de_2016:00038:805bc33dc55b","estatuto_tributario:00059:df01934516fc"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 17 → después 18 · reparación {'renamed_to_evidence_name': 19, 'rewritten_to_body': 1, 'suppressed_fragment': 3} · construidas ['artículo 85 del Estatuto Tributario', 'artículo 59 de la Ley 1819 de 2016', 'artículo 61 de la Ley 1819 de 2016', 'artículo 32 de la Ley 1819 de 2016', 'artículo 33 del Estatuto Tributario', 'Ley 863 de 2003', 'Ley 223 de 1995', 'Ley 2010 de 2019']
**Pasajes declarados por el modelo:** ['estatuto_tributario:00139:1d45173d5fa5', 'ley_1819_de_2016:00069:806b08149137', 'ley_1819_de_2016:00071:5a746eec5119', 'ley_1819_de_2016:00038:805bc33dc55b', 'estatuto_tributario:00059:df01934516fc']
**Evidencia:**
1. `estatuto_tributario:00139:1d45173d5fa5` — Estatuto Tributario (Decreto 624 de 1989) art. 85
2. `estatuto_tributario:00500:44769a16f745` — Estatuto Tributario (Decreto 624 de 1989) art. 298-6
3. `estatuto_tributario:00497:ece7ffe5206b` — Estatuto Tributario (Decreto 624 de 1989) art. 298-3
4. `ley_1819_de_2016:00069:806b08149137` — Ley 1819 de 2016 art. 59
5. `estatuto_tributario:00172:4052251b1fae` — Estatuto Tributario (Decreto 624 de 1989) art. 105
6. `ley_1819_de_2016:00071:5a746eec5119` — Ley 1819 de 2016 art. 61
7. `ley_1819_de_2016:00038:805bc33dc55b` — Ley 1819 de 2016 art. 32
8. `estatuto_tributario:00059:df01934516fc` — Estatuto Tributario (Decreto 624 de 1989) art. 33
*Tokens 5640→431 · generación 18101.99690000445 ms · retrieval 12.078400002792478 ms · grafo off*

## 168 · semi_open

**Pregunta:** ¿Cuándo procede la declaración de lesión enorme en el contrato de compraventa  de bien inmueble ?

**Medición:** cita=sin_ref_parseable · legal_basis=Sentencia del 18 de julio de 2017, de la Sala Civil de la Corte Suprema de Justicia

**Respuesta final:**
```json
{
  "respuesta": "La declaración de lesión enorme en el contrato de compraventa de bien inmueble procede cuando el precio que recibe el vendedor es inferior a la mitad del justo precio de la cosa que vende, según el artículo 1947 del Código Civil. Además, la acción rescisoria por lesión enorme expira en cuatro años, contados desde la fecha de contrato, según el artículo 1954 del Código Civil.",
  "palabras_clave": [
    "lesión enorme",
    "contrato de compraventa",
    "justo precio",
    "acción rescisoria",
    "Código Civil"
  ],
  "referencia_legal": "artículo 1947 del Código Civil; artículo 1954 del Código Civil; artículo 1946 del Código Civil; artículo 1945 del Código Civil; artículo 1892 del Código Civil; Ley 57 de 1887; Ley 6 de 1992"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La declaración de lesión enorme en el contrato de compraventa de bien inmueble procede cuando el precio que recibe el vendedor es inferior a la mitad del justo precio de la cosa que vende, según el artículo 1947 del Código Civil. Además, la acción rescisoria por lesión enorme expira en cuatro años, contados desde la fecha de contrato, según el artículo 1954 del Código Civil.","palabras_clave":["lesión enorme","contrato de compraventa","justo precio","acción rescisoria","Código Civil"],"referencia_legal":"Código Civil (Ley 84 de 1873; Ley 57 de 1887), artículo 1947 y 1954.","pasajes_usados":["codigo_civil:01945:3a0cdba094a2","codigo_civil:01952:26a8515f0a6f"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 10 → después 17 · reparación {'suppressed_fragment': 2, 'suppressed_sentence': 1} · construidas ['artículo 1947 del Código Civil', 'artículo 1954 del Código Civil', 'artículo 1946 del Código Civil', 'artículo 1945 del Código Civil', 'artículo 1892 del Código Civil', 'Ley 57 de 1887', 'Ley 6 de 1992']
**Pasajes declarados por el modelo:** ['codigo_civil:01945:3a0cdba094a2', 'codigo_civil:01952:26a8515f0a6f']
**Evidencia:**
1. `codigo_civil:01944:9564975b1998` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1946
2. `codigo_civil:01945:3a0cdba094a2` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1947
3. `codigo_civil:01952:26a8515f0a6f` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1954
4. `codigo_civil:01943:6c2405b51940` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1945
5. `codigo_civil:01890:f506f1bb7cb4` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1892
6. `codigo_civil:01947:a4557853ed02` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1949
7. `estatuto_tributario:01089:360ecf4a0a47` — Estatuto Tributario (Decreto 624 de 1989) art. 671-1
8. `codigo_general_proceso:00385:1f78135e48e8` — Código General del Proceso (Ley 1564 de 2012) art. 375
*Tokens 3620→226 · generación 8383.692699993844 ms · retrieval 7.908799991128035 ms · grafo off*

## 190 · semi_open

**Pregunta:**  ¿Cuales son los principales antecedentes fácticos que se nombran en la sentencia T-256 de 2025? 

**Medición:** cita=sin_ref_parseable · legal_basis=sentencia t-256

**Respuesta final:**
```json
{
  "respuesta": "Estas sentencias establecen que la salud es un derecho complejo que implica diversas obligaciones y acciones del Estado y la sociedad.",
  "palabras_clave": [
    "derecho a la salud",
    "jurisprudencia constitucional"
  ],
  "referencia_legal": "Sentencia T-323 de 2024; Sentencia T-350 de 2025; artículo 4 de la Ley 256 de 1996; Sentencia T-26 de 2025; Sentencia T-760 de 2008; Sentencia T-539 de 2013; Sentencia T-499 de 2014; Sentencia T-745 de 2014"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La sentencia T-256 de 2025 no menciona específicamente los antecedentes fácticos del caso en su texto proporcionado. Sin embargo, se refiere a la jurisprudencia constitucional sobre el derecho a la salud, incluyendo sentencias como T-760 de 2008, T-539 de 2013, T-499 de 2014, T-745 de 2014, C-313 de 2014, T-094 de 2016, T-014 de 2017 y T-005 de 2023. Estas sentencias establecen que la salud es un derecho complejo que implica diversas obligaciones y acciones del Estado y la sociedad. Además, se menciona la Resolución 5269 de 2017, que actualiza el Plan de Beneficios en Salud.","palabras_clave":["derecho a la salud","jurisprudencia constitucional","sentencia T-256 de 2025","Resolución 5269 de 2017"],"referencia_legal":"Sentencia T-256 de 2025, artículo 25.b, 23 y 24.1, 12, 10 y 18.","pasajes_usados":["sentencia_t_323_de_2024:00133:e060ca18b6a2"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 14 → después 9 · reparación {'emptied': 1, 'suppressed_fragment': 4, 'suppressed_sentence': 6} · construidas ['Sentencia T-323 de 2024', 'Sentencia T-350 de 2025', 'artículo 4 de la Ley 256 de 1996', 'Sentencia T-26 de 2025', 'Sentencia T-760 de 2008', 'Sentencia T-539 de 2013', 'Sentencia T-499 de 2014', 'Sentencia T-745 de 2014']
**Pasajes declarados por el modelo:** ['sentencia_t_323_de_2024:00133:e060ca18b6a2']
**Evidencia:**
1. `sentencia_t_350_de_2025:00046:3b099b6b10dd` — Sentencia T-350 de 2025 art. None
2. `ley_256_de_1996:00003:4b7dbebf3370` — Ley 256 de 1996 art. 4
3. `sentencia_t_26_de_2025:00017:93a40ff223cc` — Sentencia T-26 de 2025 art. None
4. `sentencia_t_323_de_2024:00133:e060ca18b6a2` — Sentencia T-323 de 2024 art. None
5. `sentencia_t_760_de_2008:00006:23f4f0c3c60b` — Sentencia T-760 de 2008 art. None
6. `codigo_civil:01222:59e8af3991e0` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1224
7. `sentencia_su_214_de_2016:00039:cd1edc47ad3e` — Sentencia SU-214 de 2016 art. None
8. `sentencia_c_39_de_2025:00002:662e2c65adb7` — Sentencia C-39 de 2025 art. None
*Tokens 5709→359 · generación 14399.867899992387 ms · retrieval 27.491100001498125 ms · grafo auto*

## 218 · semi_open · ABSTENCIÓN (citation_repair)

**Pregunta:** Cómo se resuelve el conflicto normativo entre la potestad del artículo 32 de la Ley 2294 de 2023 para que el Ministerio de Agricultura y Desarrollo Rural pueda expedir resoluciones donde fija el uso del suelo de los Municipios, con el artículo 313 #7 de la Constitución Política

**Medición:** cita=ref_en_evidencia_no_citada · legal_basis=Artículo 311 y 313 de la Constitución Política

**Respuesta final:**
```json
{
  "respuesta": "",
  "palabras_clave": [],
  "referencia_legal": ""
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El conflicto normativo entre la potestad del artículo 32 de la Ley 2294 de 2023 y el artículo 313 numeral 7 de la Constitución Política no se resuelve directamente en la evidencia proporcionada. La Ley 2294 de 2023 modifica el artículo 31 de la Ley 160 de 1994, permitiendo la adjudicación de tierras a juventudes rurales, mientras que el artículo 313 numeral 7 de la Constitución Política establece que la fijación del hecho gravable corresponde a la ley. La evidencia no menciona cómo se resuelve este conflicto normativo.","palabras_clave":["Ley 2294 de 2023","artículo 32","artículo 313 numeral 7","Constitución Política"],"referencia_legal":"Ley 2294 de 2023, artículo 31; Ley 160 de 1994, artículo 31; Constitución Política, artículo 313 numeral 7","pasajes_usados":["ley_2466_de_2025:00033:f119134a9e42","ley_160_de_1994:00032:4b242108cf15"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 23 → después 0 · reparación {'suppressed_fragment': 10, 'suppressed_sentence': 7} · construidas ['artículo 31 de la Ley 2466 de 2025', 'artículo 31 de la Ley 160 de 1994', 'artículo 4 de la Ley 160 de 1994', 'Sentencia C-413 de 1996', 'artículo 230 del Decreto 663 de 1993', 'Ley 1151 de 2007', 'Decreto 2363 de 2015', 'Ley 2294 de 2023']
**Pasajes declarados por el modelo:** ['ley_2466_de_2025:00033:f119134a9e42', 'ley_160_de_1994:00032:4b242108cf15']
**Evidencia:**
1. `ley_160_de_1994:00004:a84aa92e1029` — Ley 160 de 1994 art. 4
2. `ley_160_de_1994:00032:4b242108cf15` — Ley 160 de 1994 art. 31
3. `sentencia_c_413_de_1996:00001:00c586b7e483` — Sentencia C-413 de 1996 art. None
4. `decreto_663_de_1993:00325:c3b4a25e0709` — Decreto 663 de 1993 art. 230
5. `ley_1151_de_2007:00021:6cae4979a2b2` — Ley 1151 de 2007 art. 6
6. `ley_1151_de_2007:00071:5af27b6ed23e` — Ley 1151 de 2007 art. 20
7. `ley_2466_de_2025:00033:f119134a9e42` — Ley 2466 de 2025 art. 31
8. `decreto_663_de_1993:00322:f02525f5fdb8` — Decreto 663 de 1993 art. 227
*Tokens 6710→325 · generación 14147.318700008327 ms · retrieval 66.85069999366533 ms · grafo auto*

## 239 · semi_open

**Pregunta:** ¿A qué subregla jurídica llega la Corte Suprema de Justicia en relación con la renuncia a la cesantía comercial por parte del agente, en la sentencia de William Namen Vargas del 19 de octubre de 2011?

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=Artículos 1324 y 1325 del Código de Comercio. Así como en los principios de autonomía de la voluntad privada (Artículos 16, 822 y 871).

**Respuesta final:**
```json
{
  "respuesta": "La responsabilidad se fundamenta en la obligación del principal de indemnizar el daño causado por el agente directo o responsable material. Esta interpretación se alinea con la jurisprudencia reiterada en sentencias anteriores.",
  "palabras_clave": [
    "responsabilidad civil",
    "daño",
    "causalidad",
    "agente",
    "principal"
  ],
  "referencia_legal": "Sentencia SU-315 de 2025; Sentencia SU-455 de 2020; Sentencia SU-27 de 2021; Sentencia SU-149 de 2021; Sentencia SU-396 de 2024; Sentencia SC-4420 de 2020; Sentencia SC-13630 de 2015; Sentencia SC-18594 de 2016"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La Corte Suprema de Justicia en la sentencia del 19 de octubre de 2011, resalta que la renuncia a la cesantía comercial por parte del agente debe ser analizada bajo el marco de la responsabilidad civil, considerando la existencia de un daño y la causalidad entre el comportamiento del agente y el daño sufrido. La responsabilidad se fundamenta en la obligación del principal de indemnizar el daño causado por el agente directo o responsable material. Esta interpretación se alinea con la jurisprudencia reiterada en sentencias anteriores.","palabras_clave":["responsabilidad civil","daño","causalidad","agente","principal"],"referencia_legal":"Corte Suprema de Justicia, Sala de Casación Civil, Sentencia con Expediente 2005-00406-01, 18 de septiembre de 2009.","pasajes_usados":["sentencia_su_315_de_2025:00081:fd5dc0faec40","sentencia_su_315_de_2025:00086:0f49de4eb27e"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 8 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia SU-315 de 2025', 'Sentencia SU-455 de 2020', 'Sentencia SU-27 de 2021', 'Sentencia SU-149 de 2021', 'Sentencia SU-396 de 2024', 'Sentencia SC-4420 de 2020', 'Sentencia SC-13630 de 2015', 'Sentencia SC-18594 de 2016']
**Pasajes declarados por el modelo:** ['sentencia_su_315_de_2025:00081:fd5dc0faec40', 'sentencia_su_315_de_2025:00086:0f49de4eb27e']
**Evidencia:**
1. `sentencia_su_315_de_2025:00081:fd5dc0faec40` — Sentencia SU-315 de 2025 art. None
2. `sentencia_su_315_de_2025:00078:611a4fb04ffe` — Sentencia SU-315 de 2025 art. None
3. `sentencia_su_455_de_2020:00049:8d99f6702a23` — Sentencia SU-455 de 2020 art. None
4. `sentencia_su_315_de_2025:00086:0f49de4eb27e` — Sentencia SU-315 de 2025 art. None
5. `sentencia_su_27_de_2021:00039:2fa49a0a5c5a` — Sentencia SU-27 de 2021 art. None
6. `sentencia_su_149_de_2021:00057:244b602ae835` — Sentencia SU-149 de 2021 art. None
7. `sentencia_su_396_de_2024:00091:0cd6e7a617e2` — Sentencia SU-396 de 2024 art. None
8. `sentencia_su_315_de_2025:00085:7102c19939f2` — Sentencia SU-315 de 2025 art. None
*Tokens 6868→284 · generación 12621.12850000267 ms · retrieval 25.760099990293384 ms · grafo off*

## 247 · open_ended

**Pregunta:** La alcadia de bogotá a través de la secretaria de movilidad expide una resolución con el fin de ampliar la avenida 68 con sustento normativo en el articulo 2 de la constitucipon politica  el cual menciona como "fines del estado, servir a la comunidad y promover la prosperidad general y garantizar la efectividad de los principios". Lo anterior, lo afecta a usted y a la comunidad pues dicha intervención afectarpia el parque Simon Bolivar y generaria una desaparición parcial de este; además esta ampliación afecta a quienes sacan a su perro a pasear contantemente allí, las personas que se ejercitan y lo mas importante los animales que viven allí. De acuerdo a lo anterior, que acción procede ante dicha situación.

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=ley 472 de 1998 

**Respuesta final:**
```json
{
  "marco_normativo": "Constitución Política de Colombia de 1991, artículo 2, que establece que uno de los fines esenciales del Estado es servir a la comunidad, promover la prosperidad general y garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución. Además, la Constitución menciona que las autoridades están instituidas para proteger a todas las personas residentes en Colombia, incluyendo sus derechos y libertades, y para asegurar el cumplimiento de los deberes sociales del Estado y de los particulares.",
  "analisis": "Esto implica que las acciones del Estado deben estar orientadas a proteger los derechos de todos los ciudadanos, incluyendo a los animales, ya que son parte del entorno natural que debe ser protegido. La ampliación de la avenida 68, que afecta el parque Simón Bolívar y su ecosistema, podría violar este principio al dañar el entorno natural y los derechos de los animales que allí habitan. Por lo tanto, la acción que procede es la de presentar una demanda de inconstitucionalidad o una acción de tutela para proteger los derechos de la comunidad y los animales afectados.",
  "jurisprudencia": "La Sentencia C-468 de 2024 establece que las prácticas consideradas \"estéticas\" en la normativa pueden causar dolor y sufrimiento a los animales, y que estas prácticas no tienen una justificación legítima en el marco constitucional. Además, la Sentencia SU-11 de 2020 menciona que la Corte Constitucional puede revisar casos de tutela para garantizar la protección de los derechos de los ciudadanos y el entorno natural.",
  "conclusion": "La acción que procede es la de presentar una demanda de inconstitucionalidad o una acción de tutela para proteger los derechos de la comunidad y los animales afectados por la ampliación de la avenida 68, basándose en el marco normativo de la Constitución Política de Colombia de 1991 y en la jurisprudencia existente."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Constitución Política de Colombia de 1991, artículo 2, que establece que uno de los fines esenciales del Estado es servir a la comunidad, promover la prosperidad general y garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución. Además, la Constitución menciona que las autoridades están instituidas para proteger a todas las personas residentes en Colombia, incluyendo sus derechos y libertades, y para asegurar el cumplimiento de los deberes sociales del Estado y de los particulares.",
  "analisis": "La Constitución Política de Colombia de 1991, en su artículo 2, establece que uno de los fines esenciales del Estado es servir a la comunidad y garantizar la efectividad de los principios, derechos y deberes consagrados en la Constitución. Esto implica que las acciones del Estado deben estar orientadas a proteger los derechos de todos los ciudadanos, incluyendo a los animales, ya que son parte del entorno natural que debe ser protegido. La ampliación de la avenida 68, que afecta el parque Simón Bolívar y su ecosistema, podría violar este principio al dañar el entorno natural y los derechos de los animales que allí habitan. Por lo tanto, la acción que procede es la de presentar una demanda de inconstitucionalidad o una acción de tutela para proteger los derechos de la comunidad y los animales afectados.",
  "jurisprudencia": "La Sentencia C-468 de 2024 establece que las prácticas consideradas \"estéticas\" en la normativa pueden causar dolor y sufrimiento a los animales, y que estas prácticas no tienen una justificación legítima en el marco constitucional. Además, la Sentencia SU-11 de 2020 menciona que la Corte Constitucional puede revisar casos de tutela para garantizar la protección de los derechos de los ciudadanos y el entorno natural.",
  "conclusion": "La acción que procede es la de presentar una demanda de inconstitucionalidad o una acción de tutela para proteger los derechos de la comunidad y los animales afectados por la ampliación de la avenida 68, basándose en el marco normativo de la Constitución Política de Colombia de 1991 y en la jurisprudencia existente.",
  "pasajes_usados": [
    "constitucion:00001:2c8ef8b34c21",
    "sentencia_c_468_de_2024:00012:4e2ffe16f7fb",
    "sentencia_c_468_de_2024:00013:8e98ee325148",
    "sentencia_su_11_de_2020:00052:fd0b6b197421"
  ]
}
```
**Parser:** none · correcciones [] · avisos ['open_ended_analysis_sentences_4_outside_5_8']
**Citas:** antes 10 → después 7 · reparación {'suppressed_sentence': 1} · construidas ['artículo 2 de la Constitución Política', 'Sentencia C-468 de 2024', 'Sentencia SU-11 de 2020']
**Pasajes declarados por el modelo:** ['constitucion:00001:2c8ef8b34c21', 'sentencia_c_468_de_2024:00012:4e2ffe16f7fb', 'sentencia_c_468_de_2024:00013:8e98ee325148', 'sentencia_su_11_de_2020:00052:fd0b6b197421']
**Evidencia:**
1. `constitucion:00001:2c8ef8b34c21` — Constitución Política de Colombia de 1991 art. 2
2. `sentencia_c_468_de_2024:00012:4e2ffe16f7fb` — Sentencia C-468 de 2024 art. None
3. `sentencia_c_468_de_2024:00013:8e98ee325148` — Sentencia C-468 de 2024 art. None
4. `sentencia_su_11_de_2020:00052:fd0b6b197421` — Sentencia SU-11 de 2020 art. None
5. `sentencia_su_277_de_2025:00082:8b5795b538aa` — Sentencia SU-277 de 2025 art. None
6. `sentencia_c_468_de_2024:00002:0381259aadc6` — Sentencia C-468 de 2024 art. None
7. `sentencia_c_535_de_2002:00006:cb0433f9fac7` — Sentencia C-535 de 2002 art. None
8. `sentencia_su_425_de_2025:00037:64c51e08adfe` — Sentencia SU-425 de 2025 art. None
*Tokens 6402→700 · generación 29061.66750000557 ms · retrieval 78.15480000863317 ms · grafo auto*

## 253 · open_ended

**Pregunta:** El 28 de noviembre el trabajador Rodolfo Gómez se movilizaba en bus a su lugar de trabajo como cocinero. A mitad de recorrido, dado a fuertes lluvias se generó un deslizamiento que provocó que un árbol cayera encima de la parte trasera del bus en donde se encontraba el señor Gómez. Debido a esto, lo tuvieron que trasladar en ambulancia al centro médico más cercano para remitirlo a urgencias y consecuentemente se le realizaran los procedimientos necesarios.  
Ante esta situación: ¿Los accidentes ocurridos en el traslado de los trabajadores a su lugar de trabajo se reconocen como accidentes laborales? ¿Quién responde por las prestaciones económicas y asistenciales que generan de un hecho de fuerza mayor o caso fortuito? 

**Medición:** cita=cita_ok · legal_basis=Sentencia SL3385-2022.
Ley 1562 de 2012.  
artículo 56 y 57 del CST.  

**Respuesta final:**
```json
{
  "marco_normativo": "Ley 1562 de 2012, Ley 50 de 1990, Código Sustantivo del Trabajo (Decreto 2663 de 1950), Sentencia SL-3385 de 2022, Sentencia SU-396 de 2024",
  "analisis": "Según la Ley 1562 de 2012, se considera accidente de trabajo el que se produce durante el traslado de los trabajadores o contratistas desde su residencia a los lugares de trabajo o viceversa, cuando el transporte lo suministre el empleador. En el caso de Rodolfo Gómez, el traslado no fue realizado por el empleador, por lo que no se considera un accidente de trabajo. La Ley 50 de 1990 establece que el contrato de trabajo se suspende por fuerza mayor o caso fortuito que temporalmente impida su ejecución. En este caso, las fuertes lluvias y el deslizamiento que provocaron el accidente se consideran caso fortuito. La Sentencia SL-3385 de 2022 afirma que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. Por lo tanto, el accidente no se considera laboral. La Ley 1562 de 2012 también establece que el empleador y/o contratista son responsables de los gastos incurridos por la Entidad Administradora de Riesgos Laborales por causa de las prestaciones asistenciales otorgadas, así como del pago de los aportes en mora con sus respectivos intereses y el pago de las prestaciones económicas a que hubiere lugar. En este caso, el empleador debe responder por las prestaciones económicas y asistenciales generadas por el hecho de fuerza mayor o caso fortuito.",
  "jurisprudencia": "La Sentencia SL-3385 de 2022 establece que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. La Sentencia SU-396 de 2024 afirma que los trabajadores que han sufrido accidentes de trabajo tienen derecho a prestaciones asistenciales y económicas de por vida.",
  "conclusion": "Los accidentes ocurridos en el traslado de los trabajadores a su lugar de trabajo no se reconocen como accidentes laborales si el transporte no es suministrado por el empleador. Quien responde por las prestaciones económicas y asistenciales generadas por un hecho de fuerza mayor o caso fortuito es el empleador."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Ley 1562 de 2012, Ley 50 de 1990, Código Sustantivo del Trabajo (Decreto 2663 de 1950), Sentencia SL-3385 de 2022, Sentencia SU-396 de 2024",
  "analisis": "Según la Ley 1562 de 2012, se considera accidente de trabajo el que se produce durante el traslado de los trabajadores o contratistas desde su residencia a los lugares de trabajo o viceversa, cuando el transporte lo suministre el empleador. En el caso de Rodolfo Gómez, el traslado no fue realizado por el empleador, por lo que no se considera un accidente de trabajo. La Ley 50 de 1990 establece que el contrato de trabajo se suspende por fuerza mayor o caso fortuito que temporalmente impida su ejecución. En este caso, las fuertes lluvias y el deslizamiento que provocaron el accidente se consideran caso fortuito. La Sentencia SL-3385 de 2022 afirma que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. Por lo tanto, el accidente no se considera laboral. La Ley 1562 de 2012 también establece que el empleador y/o contratista son responsables de los gastos incurridos por la Entidad Administradora de Riesgos Laborales por causa de las prestaciones asistenciales otorgadas, así como del pago de los aportes en mora con sus respectivos intereses y el pago de las prestaciones económicas a que hubiere lugar. En este caso, el empleador debe responder por las prestaciones económicas y asistenciales generadas por el hecho de fuerza mayor o caso fortuito.",
  "jurisprudencia": "La Sentencia SL-3385 de 2022 establece que el accidente no se considera de origen laboral si no se produce en cumplimiento de tareas o en desarrollo de una situación excepcional creada por el empleador. La Sentencia SU-396 de 2024 afirma que los trabajadores que han sufrido accidentes de trabajo tienen derecho a prestaciones asistenciales y económicas de por vida.",
  "conclusion": "Los accidentes ocurridos en el traslado de los trabajadores a su lugar de trabajo no se reconocen como accidentes laborales si el transporte no es suministrado por el empleador. Quien responde por las prestaciones económicas y asistenciales generadas por un hecho de fuerza mayor o caso fortuito es el empleador.",
  "pasajes_usados": [
    "ley_1562_de_2012:00007:d3a8db714767",
    "ley_1562_de_2012:00005:84741522d889",
    "ley_50_de_1990:00003:f774eec2cd32",
    "sentencia_sl_3385_de_2022:00008:c03c7a4a507c",
    "sentencia_su_396_de_2024:00073:3dbf45821206"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 12 → después 12 · reparación {} · construidas ['Ley 1562 de 2012', 'artículo 4 de la Ley 50 de 1990', 'Sentencia SL-3385 de 2022']
**Pasajes declarados por el modelo:** ['ley_1562_de_2012:00007:d3a8db714767', 'ley_1562_de_2012:00005:84741522d889', 'ley_50_de_1990:00003:f774eec2cd32', 'sentencia_sl_3385_de_2022:00008:c03c7a4a507c', 'sentencia_su_396_de_2024:00073:3dbf45821206']
**Evidencia:**
1. `ley_1562_de_2012:00007:d3a8db714767` — Ley 1562 de 2012 art. 7
2. `sentencia_sl_3385_de_2022:00008:c03c7a4a507c` — Sentencia SL-3385 de 2022 art. None
3. `ley_1562_de_2012:00005:84741522d889` — Ley 1562 de 2012 art. 5
4. `ley_50_de_1990:00003:f774eec2cd32` — Ley 50 de 1990 art. 4
5. `sentencia_su_396_de_2024:00073:3dbf45821206` — Sentencia SU-396 de 2024 art. None
6. `ley_50_de_1990:00025:f81f055ba802` — Ley 50 de 1990 art. 26
7. `codigo_sustantivo_trabajo:00049:b00881778b49` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 51
8. `sentencia_sl_3385_de_2022:00004:d921a6a9b7b4` — Sentencia SL-3385 de 2022 art. None
*Tokens 6466→827 · generación 33518.45790000516 ms · retrieval 49.60620000201743 ms · grafo on*

## 272 · open_ended

**Pregunta:** Debe una Fiduciaria proceder con la entrega de recursos existentes en un patrimonio autónomo de garantía, administración y fuente de pago a la sociedad fideicomitente inmersa en un proceso de reorganización ley 1116 de 2006 o al beneficiario del contrato, cuando el juez de la SuperSociedades ha dicho que el contrato no es garantía y únicamente funciona como fuente de pago? Que parte tiene derecho sobre esos recursos ?

**Medición:** cita=cita_ok · legal_basis=Ley 1116 de 2006 y jurisprudencia de la superintendencia de sociedades en especial el auto auto No. 2025-01-730337

**Respuesta final:**
```json
{
  "marco_normativo": "Decreto 1082 de 2015, Ley 1116 de 2006, Ley 1258 de 2008, Decreto 663 de 1993, Sentencia C-207 de 2019",
  "analisis": "Según el Decreto 1082 de 2015, la sociedad fiduciaria debe cumplir con requisitos específicos al crear un patrimonio autónomo como garantía, incluyendo la obligación de realizar valoraciones periódicas y notificar la insuficiencia del patrimonio autónomo. La Ley 1116 de 2006 establece que en caso de no presentación o falta de confirmación del acuerdo de reorganización, los contratos de fiducia mercantil celebrados por el deudor se finalizan, y la restitución de los bienes se realiza bajo la supervisión del juez. La Ley 1258 de 2008 menciona que las acciones pueden estar radicadas en una fiducia mercantil, y los derechos y obligaciones del fideicomitente son ejercidos por la sociedad fiduciaria. El Decreto 663 de 1993 indica que los recursos del fideicomiso forman un patrimonio autónomo separado del de la Nación y del Banco de Comercio Exterior. La Sentencia C-207 de 2019 menciona que los recursos públicos deben ser administrados a través de un patrimonio autónomo y que la fiduciaria debe reportar información relevante a la UIAF. En el contexto de un proceso de reorganización, si el juez determina que el contrato no es garantía y solo funciona como fuente de pago, la sociedad fiduciaria debe entregar los recursos al beneficiario del contrato, ya que el patrimonio autónomo se considera propiedad del beneficiario.",
  "jurisprudencia": "No se aportó jurisprudencia.",
  "conclusion": "La sociedad fiduciaria debe entregar los recursos existentes en el patrimonio autónomo al beneficiario del contrato, ya que el juez ha determinado que el contrato no es garantía y solo funciona como fuente de pago. El patrimonio autónomo se considera propiedad del beneficiario."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Decreto 1082 de 2015, Ley 1116 de 2006, Ley 1258 de 2008, Decreto 663 de 1993, Sentencia C-207 de 2019",
  "analisis": "Según el Decreto 1082 de 2015, la sociedad fiduciaria debe cumplir con requisitos específicos al crear un patrimonio autónomo como garantía, incluyendo la obligación de realizar valoraciones periódicas y notificar la insuficiencia del patrimonio autónomo. La Ley 1116 de 2006 establece que en caso de no presentación o falta de confirmación del acuerdo de reorganización, los contratos de fiducia mercantil celebrados por el deudor se finalizan, y la restitución de los bienes se realiza bajo la supervisión del juez. La Ley 1258 de 2008 menciona que las acciones pueden estar radicadas en una fiducia mercantil, y los derechos y obligaciones del fideicomitente son ejercidos por la sociedad fiduciaria. El Decreto 663 de 1993 indica que los recursos del fideicomiso forman un patrimonio autónomo separado del de la Nación y del Banco de Comercio Exterior. La Sentencia C-207 de 2019 menciona que los recursos públicos deben ser administrados a través de un patrimonio autónomo y que la fiduciaria debe reportar información relevante a la UIAF. En el contexto de un proceso de reorganización, si el juez determina que el contrato no es garantía y solo funciona como fuente de pago, la sociedad fiduciaria debe entregar los recursos al beneficiario del contrato, ya que el patrimonio autónomo se considera propiedad del beneficiario.",
  "jurisprudencia": "No se aportó jurisprudencia.",
  "conclusion": "La sociedad fiduciaria debe entregar los recursos existentes en el patrimonio autónomo al beneficiario del contrato, ya que el juez ha determinado que el contrato no es garantía y solo funciona como fuente de pago. El patrimonio autónomo se considera propiedad del beneficiario.",
  "pasajes_usados": [
    "decreto_1082_de_2015:00182:ef633ec18771",
    "ley_1116_de_2006:00039:3405fdcac51b",
    "ley_1258_de_2008:00011:56f7de68841e",
    "decreto_663_de_1993:00420:33cc13e9205c",
    "sentencia_c_207_de_2019:00146:caa02b6f88e6"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 10 → después 10 · reparación {} · construidas ['artículo 2.2.1.2.3.3.1 del Decreto 1082 de 2015', 'artículo 38 de la Ley 1116 de 2006', 'artículo 12 de la Ley 1258 de 2008']
**Pasajes declarados por el modelo:** ['decreto_1082_de_2015:00182:ef633ec18771', 'ley_1116_de_2006:00039:3405fdcac51b', 'ley_1258_de_2008:00011:56f7de68841e', 'decreto_663_de_1993:00420:33cc13e9205c', 'sentencia_c_207_de_2019:00146:caa02b6f88e6']
**Evidencia:**
1. `decreto_1082_de_2015:00182:ef633ec18771` — Decreto 1082 de 2015 art. 2.2.1.2.3.3.1
2. `ley_1116_de_2006:00039:3405fdcac51b` — Ley 1116 de 2006 art. 38
3. `ley_1258_de_2008:00011:56f7de68841e` — Ley 1258 de 2008 art. 12
4. `ley_1116_de_2006:00052:e8ecfb330b7f` — Ley 1116 de 2006 art. 50
5. `decreto_663_de_1993:00420:33cc13e9205c` — Decreto 663 de 1993 art. 283
6. `decreto_1082_de_2015:00055:b42d9d844b35` — Decreto 1082 de 2015 art. 2.2.1.1.2.4.1
7. `sentencia_c_207_de_2019:00146:caa02b6f88e6` — Sentencia C-207 de 2019 art. None
8. `decreto_1082_de_2015:01051:20b0aa4ae460` — Decreto 1082 de 2015 art. 2.2.13.1.2.3
*Tokens 6265→724 · generación 29972.28400000313 ms · retrieval 34.44390000368003 ms · grafo off*

## 280 · semi_open

**Pregunta:** ¿Cuál es el artículo del código penal colombiano que define los requisitos que un juez debe tomar en cuenta para conceder la libertad condicional?

**Medición:** cita=cita_ok · legal_basis=Artículo 64 del código penal colombiano

**Respuesta final:**
```json
{
  "respuesta": "El artículo 64 del Código Penal (Ley 599 de 2000) define los requisitos que un juez debe tomar en cuenta para conceder la libertad condicional. Estos incluyen que la persona haya cumplido las tres quintas partes de la pena, demuestre adecuado desempeño y comportamiento durante el tratamiento penitenciario, y muestre arraigo familiar y social. Además, la concesión está supeditada a la reparación a la víctima o al aseguramiento del pago de la indemnización.",
  "palabras_clave": [
    "libertad condicional",
    "Código Penal"
  ],
  "referencia_legal": "artículo 64 del Código Penal; artículo 471 del Código de Procedimiento Penal; artículo 479 de la Ley 600 de 2000; artículo 63 del Código Penal; artículo 474 del Código de Procedimiento Penal; Ley 2098 de 2021; Ley 890 de 2004; Ley 1709 de 2014"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El artículo 64 del Código Penal (Ley 599 de 2000) define los requisitos que un juez debe tomar en cuenta para conceder la libertad condicional. Estos incluyen que la persona haya cumplido las tres quintas partes de la pena, demuestre adecuado desempeño y comportamiento durante el tratamiento penitenciario, y muestre arraigo familiar y social. Además, la concesión está supeditada a la reparación a la víctima o al aseguramiento del pago de la indemnización.","palabras_clave":["artículo 64","libertad condicional","Código Penal"],"referencia_legal":"codigo_penal:00083:d667540b7f50","pasajes_usados":["codigo_penal:00083:d667540b7f50"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 17 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 64 del Código Penal', 'artículo 471 del Código de Procedimiento Penal', 'artículo 479 de la Ley 600 de 2000', 'artículo 63 del Código Penal', 'artículo 474 del Código de Procedimiento Penal', 'Ley 2098 de 2021', 'Ley 890 de 2004', 'Ley 1709 de 2014']
**Pasajes declarados por el modelo:** ['codigo_penal:00083:d667540b7f50']
**Evidencia:**
1. `codigo_penal:00083:d667540b7f50` — Código Penal (Ley 599 de 2000) art. 64
2. `codigo_procedimiento_penal:00498:99920ea4b636` — Código de Procedimiento Penal (Ley 906 de 2004) art. 471
3. `ley_600_de_2000:00431:3b486270f6e9` — Ley 600 de 2000 art. 479
4. `codigo_penal:00082:72457621d34f` — Código Penal (Ley 599 de 2000) art. 63
5. `codigo_procedimiento_penal:00501:653e23d7f798` — Código de Procedimiento Penal (Ley 906 de 2004) art. 474
6. `ley_600_de_2000:00434:4e42c5fde7da` — Ley 600 de 2000 art. 483
7. `codigo_procedimiento_penal:00506:a3b9cfb10c76` — Código de Procedimiento Penal (Ley 906 de 2004) art. 479
8. `codigo_procedimiento_penal:00499:4c75c332783a` — Código de Procedimiento Penal (Ley 906 de 2004) art. 472
*Tokens 3338→207 · generación 7620.26650000189 ms · retrieval 30.75979999266565 ms · grafo off*

## 290 · multiple_choice · ✔ correcta

**Pregunta:** En caso de no pactar un plazo para la liquidación bilateral de un contrato Estatal sometido al Estatuto de contratación, ¿cuál sería el plazo supletorio de este?

- A: 2 años 
- B: 8 meses 
- C: 4 meses 
- D: 2 meses 

**Medición:** cita=cita_ok · legal_basis=Artículo 11 ley 1150 de 2007

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "La pregunta se refiere al plazo supletorio para la liquidación bilateral de un contrato Estatal cuando no se pacta un plazo en los pliegos de condiciones. De acuerdo con el artículo 11 de la Ley 1150 de 2007, si no existe un término fijado en los pliegos de condiciones o sus equivalentes, la liquidación se realizará dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga. Por lo tanto, el plazo supletorio es de 4 meses. Fundamento normativo: artículo 2.2.1.1.2.1.2 del Decreto 1082 de 2015; artículo 2.2.1.2.3.1.3 del Decreto 1082 de 2015; artículo 2.2.1.2.3.1.18 del Decreto 1082 de 2015; artículo 2.2.2.1.5.11 del Decreto 1082 de 2015; Decreto 1510 de 2013; Ley 1508 de 2012; Decreto 438 de 2021.",
  "descarte_opciones": {
    "A": "No se menciona en la norma",
    "B": "No se menciona en la norma",
    "D": "No se menciona en la norma"
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La pregunta se refiere al plazo supletorio para la liquidación bilateral de un contrato Estatal cuando no se pacta un plazo en los pliegos de condiciones. De acuerdo con el artículo 11 de la Ley 1150 de 2007, si no existe un término fijado en los pliegos de condiciones o sus equivalentes, la liquidación se realizará dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga. Por lo tanto, el plazo supletorio es de 4 meses.","respuesta_correcta":"C","descarte_opciones":{"A":"No se menciona en la norma","B":"No se menciona en la norma","D":"No se menciona en la norma"},"pasajes_usados":["ley_1150_de_2007:00020:a442ace14a36"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 13 · reparación {} · construidas ['artículo 11 de la Ley 1150 de 2007', 'artículo 2.2.1.1.2.1.2 del Decreto 1082 de 2015', 'artículo 2.2.1.2.3.1.3 del Decreto 1082 de 2015', 'artículo 2.2.1.2.3.1.18 del Decreto 1082 de 2015', 'artículo 2.2.2.1.5.11 del Decreto 1082 de 2015', 'Decreto 1510 de 2013', 'Ley 1508 de 2012', 'Decreto 438 de 2021']
**Pasajes declarados por el modelo:** ['ley_1150_de_2007:00020:a442ace14a36']
**Evidencia:**
1. `decreto_1082_de_2015:00040:ae5297bce595` — Decreto 1082 de 2015 art. 2.2.1.1.2.1.2
2. `decreto_1082_de_2015:00154:24b44755c8b5` — Decreto 1082 de 2015 art. 2.2.1.2.3.1.3
3. `ley_1150_de_2007:00020:a442ace14a36` — Ley 1150 de 2007 art. 11
4. `decreto_1082_de_2015:00169:de0e0b06e4cf` — Decreto 1082 de 2015 art. 2.2.1.2.3.1.18
5. `decreto_1082_de_2015:00286:3139d30e8aaa` — Decreto 1082 de 2015 art. 2.2.2.1.5.11
6. `sentencia_c_207_de_2019:00034:dfe3789e0c02` — Sentencia C-207 de 2019 art. None
7. `decreto_1082_de_2015:00301:8dd4330675f0` — Decreto 1082 de 2015 art. 2.2.2.1.8.3
8. `decreto_1082_de_2015:00031:ebe4765c5d2d` — Decreto 1082 de 2015 art. 2.2.1.1.1.6.4
*Tokens 5564→244 · generación 9991.10839999048 ms · retrieval 76.02700000279583 ms · grafo off*

## 308 · multiple_choice · ✔ correcta

**Pregunta:** ¿Cuál es el plazo de liquidación del contrato de manera unilateral?


- A: 2 meses
- B: No hay plazo
- C: Dos años
- D: 4 meses

**Medición:** cita=sin_ref_parseable · legal_basis=Art 44 ley 1150 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "C. A. Por lo tanto, el plazo de liquidación del contrato de manera unilateral es de 2 meses. Fundamento normativo: artículo 11 de la Ley 1150 de 2007; artículo 5 de la Ley 50 de 1990; artículo 16 de la Ley 80 de 1993; artículo 61 del Código Sustantivo del Trabajo; Sentencia C-207 de 2019; Decreto 2351 de 1965; Sentencia C-16 de 1998; Sentencia C-1507 de 2000.",
  "descarte_opciones": {
    "B": "No hay plazo: Esto es incorrecto, ya que el artículo 11 de la Ley 1150 de 2007 establece un plazo de 2 meses para la liquidación unilateral.",
    "C": "C. A.",
    "D": "4 meses: Esto es incorrecto, ya que el plazo de 4 meses se refiere a la liquidación dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "De acuerdo con el artículo 11 de la Ley 1150 de 2007, si el contratista no se presenta a la liquidación previa notificación o convocatoria que le haga la entidad, o las partes no lleguen a un acuerdo sobre su contenido, la entidad tendrá la facultad de liquidar en forma unilateral dentro de los dos (2) meses siguientes, de conformidad con lo dispuesto en el artículo 136 del C. C. A. Por lo tanto, el plazo de liquidación del contrato de manera unilateral es de 2 meses.",
  "respuesta_correcta": "A",
  "descarte_opciones": {
    "B": "No hay plazo: Esto es incorrecto, ya que el artículo 11 de la Ley 1150 de 2007 establece un plazo de 2 meses para la liquidación unilateral.",
    "C": "Dos años: Esto es incorrecto, ya que el plazo de dos años se refiere a la liquidación en cualquier tiempo dentro de los dos años siguientes al vencimiento del término a que se refieren los incisos anteriores, de mutuo acuerdo o unilateralmente, sin perjuicio de lo previsto en el artículo 136 del C. C. A.",
    "D": "4 meses: Esto es incorrecto, ya que el plazo de 4 meses se refiere a la liquidación dentro de los cuatro (4) meses siguientes a la expiración del término previsto para la ejecución del contrato o a la expedición del acto administrativo que ordene la terminación, o a la fecha del acuerdo que la disponga."
  },
  "pasajes_usados": [
    "ley_1150_de_2007:00020:a442ace14a36"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 6 → después 14 · reparación {'suppressed_sentence': 2} · construidas ['artículo 11 de la Ley 1150 de 2007', 'artículo 5 de la Ley 50 de 1990', 'artículo 16 de la Ley 80 de 1993', 'artículo 61 del Código Sustantivo del Trabajo', 'Sentencia C-207 de 2019', 'Decreto 2351 de 1965', 'Sentencia C-16 de 1998', 'Sentencia C-1507 de 2000']
**Pasajes declarados por el modelo:** ['ley_1150_de_2007:00020:a442ace14a36']
**Evidencia:**
1. `ley_1150_de_2007:00020:a442ace14a36` — Ley 1150 de 2007 art. 11
2. `ley_50_de_1990:00004:d1a5e529e3e6` — Ley 50 de 1990 art. 5
3. `ley_80_de_1993:00021:e5d787cb298e` — Ley 80 de 1993 art. 16
4. `codigo_sustantivo_trabajo:00060:7142bbd6ef28` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 61
5. `sentencia_c_207_de_2019:00079:6babc1b45b07` — Sentencia C-207 de 2019 art. None
6. `cpaca:00179:7b13bd2bf137` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 164
7. `sentencia_c_207_de_2019:00101:675156a88518` — Sentencia C-207 de 2019 art. None
8. `sentencia_c_207_de_2019:00027:99881ee5b5f7` — Sentencia C-207 de 2019 art. None
*Tokens 6364→421 · generación 18264.13509999111 ms · retrieval 43.994699997710995 ms · grafo off*

## 352 · multiple_choice · ✔ correcta

**Pregunta:** La Corte Constitucional de Colombia puede decretar la nulidad de los procesos que tramita cuando:

- A: Exista desacuerdo sobre la ponencia debatida
- B: Se acredite una violación del debido proceso
- C: No haya quórum para discutir la ponencia bajo revisión
- D: Así lo solicite cualquier ciudadano

**Medición:** cita=cita_ok · legal_basis=Decreto 2067 de 1991, art. 49 (nulidad por violación del debido proceso).

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "La evidencia indica que la Corte Constitucional puede decretar la nulidad de los procesos que tramita cuando se acredite una violación del debido proceso. Esto se fundamenta en el artículo 49 del decreto 2067 de 1991, que establece que la nulidad de los procesos ante la Corte Constitucional solo podrá ser alegada antes de proferido el fallo y que solo las irregularidades que impliquen violación del debido proceso podrán servir de base para que el Pleno de la Corte anule el proceso. Además, la Sentencia C-239 de 1997 menciona que la nulidad puede ser solicitada por irregularidades que impliquen violación del debido proceso, y que estas deben ser significativas y trascendentes para que la petición de nulidad pueda prosperar. Por lo tanto, la opción correcta es B. Fundamento normativo: Sentencia C-355 de 2006; artículo 1914 del Código de Comercio; Sentencia SU-214 de 2016; Constitución Política; Sentencia C-1299 de 2005; Sentencia C-1300 de 2005.",
  "descarte_opciones": {
    "A": "No se menciona desacuerdo sobre la ponencia debatida como causa de nulidad.",
    "C": "No se menciona quórum como causa de nulidad.",
    "D": "No se menciona que así lo solicite cualquier ciudadano como causa de nulidad."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La evidencia indica que la Corte Constitucional puede decretar la nulidad de los procesos que tramita cuando se acredite una violación del debido proceso. Esto se fundamenta en el artículo 49 del decreto 2067 de 1991, que establece que la nulidad de los procesos ante la Corte Constitucional solo podrá ser alegada antes de proferido el fallo y que solo las irregularidades que impliquen violación del debido proceso podrán servir de base para que el Pleno de la Corte anule el proceso. Además, la Sentencia C-239 de 1997 menciona que la nulidad puede ser solicitada por irregularidades que impliquen violación del debido proceso, y que estas deben ser significativas y trascendentes para que la petición de nulidad pueda prosperar. Por lo tanto, la opción correcta es B.","respuesta_correcta":"B","descarte_opciones":{"A":"No se menciona desacuerdo sobre la ponencia debatida como causa de nulidad.","C":"No se menciona quórum como causa de nulidad.","D":"No se menciona que así lo solicite cualquier ciudadano como causa de nulidad."},"pasajes_usados":["decreto_2067_de_1991:00048:2a53e2667adc","sentencia_c_239_de_1997:00085:bff064fc20f4","sentencia_c_239_de_1997:00084:9b3f9fad0f54"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 10 · reparación {} · construidas ['artículo 49 del Decreto 2067 de 1991', 'Sentencia C-239 de 1997', 'Sentencia C-355 de 2006', 'artículo 1914 del Código de Comercio', 'Sentencia SU-214 de 2016', 'Constitución Política', 'Sentencia C-1299 de 2005', 'Sentencia C-1300 de 2005']
**Pasajes declarados por el modelo:** ['decreto_2067_de_1991:00048:2a53e2667adc', 'sentencia_c_239_de_1997:00085:bff064fc20f4', 'sentencia_c_239_de_1997:00084:9b3f9fad0f54']
**Evidencia:**
1. `sentencia_c_239_de_1997:00085:bff064fc20f4` — Sentencia C-239 de 1997 art. None
2. `sentencia_c_239_de_1997:00084:9b3f9fad0f54` — Sentencia C-239 de 1997 art. None
3. `sentencia_c_355_de_2006:00256:2c38f21835ef` — Sentencia C-355 de 2006 art. None
4. `sentencia_c_239_de_1997:00097:492283098fdb` — Sentencia C-239 de 1997 art. None
5. `decreto_2067_de_1991:00048:2a53e2667adc` — Decreto 2067 de 1991 art. 49
6. `codigo_comercio:01989:5e28bef5c68b` — Código de Comercio (Decreto 410 de 1971) art. 1914
7. `sentencia_c_239_de_1997:00102:7f429cd67b33` — Sentencia C-239 de 1997 art. None
8. `sentencia_su_214_de_2016:00217:89ed0ec89393` — Sentencia SU-214 de 2016 art. None
*Tokens 7029→389 · generación 16961.951799996314 ms · retrieval 63.190300003043376 ms · grafo off*

## 358 · multiple_choice · ✘ esperada D

**Pregunta:** Conforme a la tradición civilista (civil law), ¿qué mecanismo procesal se encuentra previsto para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes?

- A: Ninguna de las anteriores.
- B: Acción posesoria.
- C: Acción resolutoria.
- D: Acción reivindicatoria.

**Medición:** cita=cita_ok · legal_basis=c) Acción reivindicatoria, disponible únicamente para los dueños legales del bien, de acuerdo con el artículo 946 del C.C.


**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "La Sentencia SU-214 de 2016 menciona que en los países de tradición civilista, como Colombia, las Cortes tienen el poder constitucional para invalidar la discriminación legal. Esto implica que en el sistema jurídico colombiano, se permite a las Cortes Constitucionales actuar para corregir situaciones de ilegalidad o discriminación, incluyendo la usurpación o transferencia ilegal de bienes. Sin embargo, el mecanismo procesal específico para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes no se menciona directamente en los pasajes proporcionados. La Sentencia T-77 de 2025 no aborda este tema. Por lo tanto, la opción correcta es la que indica que no hay mecanismo procesal previsto para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes, ya que no se menciona directamente en los pasajes proporcionados. Fundamento normativo: artículo 571 del Código General del Proceso; artículo 33 de la Ley 160 de 1994; artículo 384 del Código General del Proceso; Código Civil; Ley 1116 de 2006; Decreto 508 de 1974.",
  "descarte_opciones": {
    "B": "La acción posesoria se refiere a la recuperación de un bien por prescripción, lo cual no se menciona directamente en los pasajes proporcionados.",
    "C": "La acción resolutoria se refiere a la anulación de un acto jurídico, lo cual no se menciona directamente en los pasajes proporcionados.",
    "D": "La acción reivindicatoria se refiere a la recuperación de un bien por el derecho de propiedad, lo cual no se menciona directamente en los pasajes proporcionados."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La Sentencia SU-214 de 2016 menciona que en los países de tradición civilista, como Colombia, las Cortes tienen el poder constitucional para invalidar la discriminación legal. Esto implica que en el sistema jurídico colombiano, se permite a las Cortes Constitucionales actuar para corregir situaciones de ilegalidad o discriminación, incluyendo la usurpación o transferencia ilegal de bienes. Por otro lado, el Código General del Proceso (Ley 1564 de 2012) en su artículo 571 establece los efectos de la adjudicación, lo cual se relaciona con la restitución de bienes. Sin embargo, el mecanismo procesal específico para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes no se menciona directamente en los pasajes proporcionados. La Sentencia T-77 de 2025 no aborda este tema. Por lo tanto, la opción correcta es la que indica que no hay mecanismo procesal previsto para reclamar la restitución derivada de una usurpación o transferencia ilegal de bienes, ya que no se menciona directamente en los pasajes proporcionados.","respuesta_correcta":"A","descarte_opciones":{"B":"La acción posesoria se refiere a la recuperación de un bien por prescripción, lo cual no se menciona directamente en los pasajes proporcionados.","C":"La acción resolutoria se refiere a la anulación de un acto jurídico, lo cual no se menciona directamente en los pasajes proporcionados.","D":"La acción reivindicatoria se refiere a la recuperación de un bien por el derecho de propiedad, lo cual no se menciona directamente en los pasajes proporcionados."},"pasajes_usados":["sentencia_su_214_de_2016:00184:fcaf8421c912","codigo_general_proceso:00593:c1edf5972d50"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 11 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia SU-214 de 2016', 'artículo 571 del Código General del Proceso', 'artículo 33 de la Ley 160 de 1994', 'Sentencia T-77 de 2025', 'artículo 384 del Código General del Proceso', 'Código Civil', 'Ley 1116 de 2006', 'Decreto 508 de 1974']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00184:fcaf8421c912', 'codigo_general_proceso:00593:c1edf5972d50']
**Evidencia:**
1. `sentencia_su_214_de_2016:00184:fcaf8421c912` — Sentencia SU-214 de 2016 art. None
2. `ley_160_de_1994:00040:137fbbf11276` — Ley 160 de 1994 art. 33
3. `sentencia_t_77_de_2025:00026:131cfcc7f11e` — Sentencia T-77 de 2025 art. None
4. `codigo_general_proceso:00396:a7ec72cd2300` — Código General del Proceso (Ley 1564 de 2012) art. 384
5. `codigo_comercio:01763:9fce23dd9450` — Código de Comercio (Decreto 410 de 1971) art. 1687
6. `codigo_procedimiento_penal:00075:34b0feb2b224` — Código de Procedimiento Penal (Ley 906 de 2004) art. 74
7. `codigo_general_proceso:00593:c1edf5972d50` — Código General del Proceso (Ley 1564 de 2012) art. 571
8. `codigo_civil:00971:8f1814731196` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 973
*Tokens 7091→476 · generación 20619.80409998796 ms · retrieval 55.42319999949541 ms · grafo off*

## 442 · semi_open

**Pregunta:** Cité un fragmento de el artículo 60 del código sustantivo del trabajo que menciona la prohibición al trabajador de disminuir el ritmo de trabajo.

**Medición:** cita=cita_ok · legal_basis=El Código sustantivo del trabajo 

**Respuesta final:**
```json
{
  "respuesta": "El artículo 60 del Código Sustantivo del Trabajo (Decreto 2663 de 1950) prohíbe al trabajador disminuir intencionalmente el ritmo de ejecución del trabajo, suspender labores, promover suspensiones intempestivas del trabajo o excitar a su declaración o mantenimiento, sea que participe o no en ellas.",
  "palabras_clave": [
    "Código Sustantivo del Trabajo",
    "prohibición",
    "ritmo de trabajo"
  ],
  "referencia_legal": "artículo 60 del Código Sustantivo del Trabajo; artículo 343 del Código Sustantivo del Trabajo; artículo 65 del Código Sustantivo del Trabajo; artículo 136 del Código Sustantivo del Trabajo; Ley 2141 de 2021; Sentencia C-781 de 2003; Sentencia C-892 de 2009; Ley 789 de 2002"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El artículo 60 del Código Sustantivo del Trabajo (Decreto 2663 de 1950) prohíbe al trabajador disminuir intencionalmente el ritmo de ejecución del trabajo, suspender labores, promover suspensiones intempestivas del trabajo o excitar a su declaración o mantenimiento, sea que participe o no en ellas.","palabras_clave":["artículo 60","Código Sustantivo del Trabajo","prohibición","ritmo de trabajo"],"referencia_legal":"codigo_sustantivo_trabajo:00059:fa8d3365aa21","pasajes_usados":["codigo_sustantivo_trabajo:00059:fa8d3365aa21"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_1_outside_3_5']
**Citas:** antes 5 → después 16 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 60 del Código Sustantivo del Trabajo', 'artículo 343 del Código Sustantivo del Trabajo', 'artículo 65 del Código Sustantivo del Trabajo', 'artículo 136 del Código Sustantivo del Trabajo', 'Ley 2141 de 2021', 'Sentencia C-781 de 2003', 'Sentencia C-892 de 2009', 'Ley 789 de 2002']
**Pasajes declarados por el modelo:** ['codigo_sustantivo_trabajo:00059:fa8d3365aa21']
**Evidencia:**
1. `codigo_sustantivo_trabajo:00059:fa8d3365aa21` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 60
2. `codigo_sustantivo_trabajo:00355:38750db83bb3` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 343
3. `codigo_sustantivo_trabajo:00065:3a1c4bd7813c` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 65
4. `codigo_sustantivo_trabajo:00137:ade6fe19a20d` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 136
5. `ley_2141_de_2021:00000:c6a5d7ead9bb` — Ley 2141 de 2021 art. 1
6. `ley_2466_de_2025:00051:0ff973653e2d` — Ley 2466 de 2025 art. 48
7. `codigo_sustantivo_trabajo:00150:b09b99550711` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 149
8. `ley_50_de_1990:00036:059f731c17e6` — Ley 50 de 1990 art. 37
*Tokens 4885→185 · generación 7335.4896000091685 ms · retrieval 25.56650000042282 ms · grafo off*

## 453 · semi_open

**Pregunta:** ¿Cuál es el principal precedente jurisprudencial en Colombia sobre el reconocimiento de los animales como seres sintientes? 

**Medición:** cita=cita_ok · legal_basis=Sentencia C-468 de 2024, sentencia C-332 de 2025 y SU-016 de 2020

**Respuesta final:**
```json
{
  "respuesta": "El principal precedente jurisprudencial en Colombia sobre el reconocimiento de los animales como seres sintientes es la Sentencia SU-16 de 2020. En esta sentencia, la Corte Constitucional establece que los animales son seres sintientes con valor propio, lo cual les otorga derechos y obligaciones de protección.",
  "palabras_clave": [
    "Sentencia SU-16 de 2020",
    "seres sintientes",
    "protección animal",
    "derechos animales",
    "Corte Constitucional"
  ],
  "referencia_legal": "Sentencia SU-16 de 2020; Sentencia C-468 de 2024; Sentencia C-332 de 2025; Sentencia C-55 de 2022; Ley 84 de 1989; Constitución Política; Sentencia C-355 de 2006"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "El principal precedente jurisprudencial en Colombia sobre el reconocimiento de los animales como seres sintientes es la Sentencia SU-16 de 2020. En esta sentencia, la Corte Constitucional establece que los animales son seres sintientes con valor propio, lo cual les otorga derechos y obligaciones de protección. Esta decisión se fundamenta en la Constitución y en la jurisprudencia que reconoce la capacidad de los animales para sentir dolor y sufrimiento, lo cual implica una prohibición de maltrato y un imperativo de bienestar animal.",
  "palabras_clave": ["Sentencia SU-16 de 2020", "seres sintientes", "protección animal", "derechos animales", "Corte Constitucional"],
  "referencia_legal": "Sentencia SU-16 de 2020, artículo 3.2.1 y 3.2.2",
  "pasajes_usados": [
    "sentencia_su_16_de_2020:00017:3d229478a611",
    "sentencia_su_16_de_2020:00102:5b8333b9b73a",
    "sentencia_su_16_de_2020:00109:d4312efad931"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 6 → después 9 · reparación {'rewritten_to_body': 1, 'suppressed_sentence': 1} · construidas ['Sentencia SU-16 de 2020', 'Sentencia C-468 de 2024', 'Sentencia C-332 de 2025', 'Sentencia C-55 de 2022', 'Ley 84 de 1989', 'Constitución Política', 'Sentencia C-355 de 2006']
**Pasajes declarados por el modelo:** ['sentencia_su_16_de_2020:00017:3d229478a611', 'sentencia_su_16_de_2020:00102:5b8333b9b73a', 'sentencia_su_16_de_2020:00109:d4312efad931']
**Evidencia:**
1. `sentencia_su_16_de_2020:00017:3d229478a611` — Sentencia SU-16 de 2020 art. None
2. `sentencia_su_16_de_2020:00102:5b8333b9b73a` — Sentencia SU-16 de 2020 art. None
3. `sentencia_c_468_de_2024:00013:8e98ee325148` — Sentencia C-468 de 2024 art. None
4. `sentencia_c_332_de_2025:00032:fc4390247b97` — Sentencia C-332 de 2025 art. None
5. `sentencia_c_55_de_2022:00330:a814c9c40c7c` — Sentencia C-55 de 2022 art. None
6. `sentencia_c_332_de_2025:00048:0d30a5834964` — Sentencia C-332 de 2025 art. None
7. `sentencia_su_16_de_2020:00109:d4312efad931` — Sentencia SU-16 de 2020 art. None
8. `sentencia_c_468_de_2024:00022:828a165888bb` — Sentencia C-468 de 2024 art. None
*Tokens 7588→336 · generación 14734.55290000129 ms · retrieval 14.6723999932874 ms · grafo off*

## 472 · semi_open

**Pregunta:** Cuales son los requisitos que exige la ley para el control de integraciones empresariales? 

**Medición:** cita=cita_ok · legal_basis=Ley 1340 de 2009

**Respuesta final:**
```json
{
  "respuesta": "La ley establece que las empresas que se dediquen a la misma actividad económica o participen en la misma cadena de valor, y que cumplan con ciertas condiciones, estarán obligadas a informar sobre operaciones de integración empresarial. Estas condiciones incluyen tener ingresos operacionales o activos totales superiores a un monto determinado por la Superintendencia de Industria y Comercio. Además, en algunos casos, se requiere la notificación previa a la Superintendencia de Industria y Comercio.",
  "palabras_clave": [
    "control de integraciones empresariales",
    "ingresos operacionales",
    "activos totales",
    "Superintendencia de Industria y Comercio"
  ],
  "referencia_legal": "artículo 9 de la Ley 1340 de 2009; artículo 33 de la Ley 1340 de 2009; artículo 46 del Decreto 2153 de 1992; artículo 2 de la Ley 1340 de 2009; artículo 8 de la Ley 1340 de 2009; Ley 155 de 1959; Ley 222 de 1995; Código Civil"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La ley establece que las empresas que se dediquen a la misma actividad económica o participen en la misma cadena de valor, y que cumplan con ciertas condiciones, estarán obligadas a informar sobre operaciones de integración empresarial. Estas condiciones incluyen tener ingresos operacionales o activos totales superiores a un monto determinado por la Superintendencia de Industria y Comercio. Además, en algunos casos, se requiere la notificación previa a la Superintendencia de Industria y Comercio.","palabras_clave":["control de integraciones empresariales","ingresos operacionales","activos totales","Superintendencia de Industria y Comercio"],"referencia_legal":"ley_1340_de_2009:00008:d7e885341c50","pasajes_usados":["ley_1340_de_2009:00008:d7e885341c50"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 0 → después 13 · reparación {} · construidas ['artículo 9 de la Ley 1340 de 2009', 'artículo 33 de la Ley 1340 de 2009', 'artículo 46 del Decreto 2153 de 1992', 'artículo 2 de la Ley 1340 de 2009', 'artículo 8 de la Ley 1340 de 2009', 'Ley 155 de 1959', 'Ley 222 de 1995', 'Código Civil']
**Pasajes declarados por el modelo:** ['ley_1340_de_2009:00008:d7e885341c50']
**Evidencia:**
1. `ley_1340_de_2009:00033:43459ffa1f51` — Ley 1340 de 2009 art. 33
2. `decreto_2153_de_1992:00049:7821acf23781` — Decreto 2153 de 1992 art. 46
3. `ley_1340_de_2009:00001:8f7ee6104e47` — Ley 1340 de 2009 art. 2
4. `ley_1340_de_2009:00007:d5ae8eeb6058` — Ley 1340 de 2009 art. 8
5. `ley_1340_de_2009:00008:d7e885341c50` — Ley 1340 de 2009 art. 9
6. `codigo_comercio:00484:fe9b95b24867` — Código de Comercio (Decreto 410 de 1971) art. 476
7. `estatuto_tributario:00956:16afc95d6550` — Estatuto Tributario (Decreto 624 de 1989) art. 587-1
8. `ley_1116_de_2006:00001:b0804ab86185` — Ley 1116 de 2006 art. 2
*Tokens 4155→235 · generación 9538.294800004223 ms · retrieval 18.936199994641356 ms · grafo off*

## 487 · multiple_choice · ✔ correcta

**Pregunta:** ¿Qué es la disolución de la sociedad conyugal?

- A: La declaración de que la sociedad conyugal ha terminado. 
- B: Un requisito para la liquidación. 
- C: Una forma más rápida para divorciarse. 
- D: La liquidación de la sociedad conyugal. 

**Medición:** cita=cita_ok · legal_basis=1820 del Código Civil. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "La disolución de la sociedad conyugal se refiere a la terminación de la relación jurídica entre los cónyuges. Según el artículo 1820 del Código Civil, la sociedad conyugal se disuelve por diversos motivos, entre ellos la disolución del matrimonio, la separación judicial de cuerpos, la sentencia de separación de bienes, la declaración de nulidad del matrimonio y el mutuo acuerdo de los cónyuges. Por lo tanto, la disolución de la sociedad conyugal es la terminación de esta relación, lo que se refleja en la opción A. Las otras opciones no definen correctamente la disolución de la sociedad conyugal, ya que una liquidación es un proceso posterior a la disolución, un requisito no es la definición de la disolución, y una forma más rápida para divorciarse no se menciona en la evidencia. Fundamento normativo: artículo 523 del Código General del Proceso; artículo 69 de la Ley 2220 de 2022; artículo 22 del Código General del Proceso; artículo 23 del Código General del Proceso; Ley 57 de 1887; Ley 1996 de 2019; Ley 2447 de 2025.",
  "descarte_opciones": {
    "B": "Un requisito para la liquidación no define la disolución de la sociedad conyugal.",
    "C": "Una forma más rápida para divorciarse no se menciona en la evidencia.",
    "D": "La liquidación de la sociedad conyugal es un proceso posterior a la disolución."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La disolución de la sociedad conyugal se refiere a la terminación de la relación jurídica entre los cónyuges. Según el artículo 1820 del Código Civil, la sociedad conyugal se disuelve por diversos motivos, entre ellos la disolución del matrimonio, la separación judicial de cuerpos, la sentencia de separación de bienes, la declaración de nulidad del matrimonio y el mutuo acuerdo de los cónyuges. Por lo tanto, la disolución de la sociedad conyugal es la terminación de esta relación, lo que se refleja en la opción A. Las otras opciones no definen correctamente la disolución de la sociedad conyugal, ya que una liquidación es un proceso posterior a la disolución, un requisito no es la definición de la disolución, y una forma más rápida para divorciarse no se menciona en la evidencia.","respuesta_correcta":"A","descarte_opciones":{"B":"Un requisito para la liquidación no define la disolución de la sociedad conyugal.","C":"Una forma más rápida para divorciarse no se menciona en la evidencia.","D":"La liquidación de la sociedad conyugal es un proceso posterior a la disolución."},"pasajes_usados":["codigo_civil:01818:faa724d12b7e"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 13 · reparación {} · construidas ['artículo 1820 del Código Civil', 'artículo 523 del Código General del Proceso', 'artículo 69 de la Ley 2220 de 2022', 'artículo 22 del Código General del Proceso', 'artículo 23 del Código General del Proceso', 'Ley 57 de 1887', 'Ley 1996 de 2019', 'Ley 2447 de 2025']
**Pasajes declarados por el modelo:** ['codigo_civil:01818:faa724d12b7e']
**Evidencia:**
1. `codigo_civil:01818:faa724d12b7e` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1820
2. `codigo_general_proceso:00543:e619df7325af` — Código General del Proceso (Ley 1564 de 2012) art. 523
3. `ley_2220_de_2022:00071:8788a8bab59a` — Ley 2220 de 2022 art. 69
4. `codigo_general_proceso:00021:52321c1b4f18` — Código General del Proceso (Ley 1564 de 2012) art. 22
5. `codigo_general_proceso:00022:6044d07399d7` — Código General del Proceso (Ley 1564 de 2012) art. 23
6. `codigo_civil:01793:78aa9859c8cb` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1795
7. `ley_640_de_2001:00039:3ed05ab97955` — Ley 640 de 2001 art. 40
8. `ley_979_de_2005:00003:e88f9f2136f2` — Ley 979 de 2005 art. 4
*Tokens 5469→307 · generación 12468.612100012251 ms · retrieval 15.473499996005557 ms · grafo off*

## 490 · semi_open

**Pregunta:** ¿Qué comprende los pasivos de la sociedad conyugal?

**Medición:** cita=cita_ok · legal_basis=1796 del Código Civil. 

**Respuesta final:**
```json
{
  "respuesta": "Los pasivos de la sociedad conyugal comprenden las obligaciones que consten en título que preste mérito ejecutivo, siempre que en la audiencia no se objeten, y las que a pesar de no tener dicha calidad se acepten expresamente en ella por todos los herederos o por estos y por el cónyuge o compañero permanente, cuando conciernan a la sociedad conyugal o patrimonial. También se incluyen los créditos de los acreedores que concurran a la audiencia.",
  "palabras_clave": [
    "sociedad conyugal",
    "pasivos",
    "obligaciones",
    "acreedores",
    "audiencia"
  ],
  "referencia_legal": "artículo 501 del Código General del Proceso; artículo 523 del Código General del Proceso; artículo 1820 del Código Civil; artículo 1774 del Código Civil; artículo 1804 del Código Civil; Ley 28 de 1932; Ley 57 de 1887; Constitución Política"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "Los pasivos de la sociedad conyugal comprenden las obligaciones que consten en título que preste mérito ejecutivo, siempre que en la audiencia no se objeten, y las que a pesar de no tener dicha calidad se acepten expresamente en ella por todos los herederos o por estos y por el cónyuge o compañero permanente, cuando conciernan a la sociedad conyugal o patrimonial. También se incluyen los créditos de los acreedores que concurran a la audiencia.",
  "palabras_clave": ["sociedad conyugal", "pasivos", "obligaciones", "acreedores", "audiencia"],
  "referencia_legal": "Código General del Proceso (Ley 1564 de 2012), Artículo 501",
  "pasajes_usados": ["codigo_general_proceso:00520:e40d313ec22c"]
}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 3 → después 13 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 501 del Código General del Proceso', 'artículo 523 del Código General del Proceso', 'artículo 1820 del Código Civil', 'artículo 1774 del Código Civil', 'artículo 1804 del Código Civil', 'Ley 28 de 1932', 'Ley 57 de 1887', 'Constitución Política']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00520:e40d313ec22c']
**Evidencia:**
1. `codigo_general_proceso:00543:e619df7325af` — Código General del Proceso (Ley 1564 de 2012) art. 523
2. `codigo_general_proceso:00520:e40d313ec22c` — Código General del Proceso (Ley 1564 de 2012) art. 501
3. `codigo_civil:01818:faa724d12b7e` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1820
4. `codigo_civil:01772:f917f7612f99` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1774
5. `codigo_civil:01802:77320bb0024b` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1804
6. `codigo_civil:00867:8c171df1ee08` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 869
7. `codigo_civil:01236:e294f9a6ae57` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1238
8. `codigo_general_proceso:00022:6044d07399d7` — Código General del Proceso (Ley 1564 de 2012) art. 23
*Tokens 4708→225 · generación 9557.436800008873 ms · retrieval 3.8459999923361465 ms · grafo off*

## 513 · open_ended

**Pregunta:** ¿Cómo debería actuar una empresa si esta decide ingresar de manera legal su producto a un país para generar una venta y el consumidor final decide revender dicho producto? ¿ Es posible que la empresa prohíba la venta por segunda vez? 

**Medición:** cita=sin_ref_parseable · legal_basis=https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf 

**Respuesta final:**
```json
{
  "marco_normativo": "Estatuto del Consumidor (Ley 1480 de 2011) y otros marcos normativos aplicables.",
  "analisis": "El Estatuto del Consumidor (Ley 1480 de 2011) establece que el consumidor tiene derechos sobre los productos que adquiere, incluyendo la posibilidad de resolver el contrato si el producto no se entrega en el plazo acordado o no corresponde a lo solicitado. Sin embargo, no se menciona explícitamente la prohibición de revender un producto adquirido. La prohibición de revender un producto depende de los términos del contrato entre la empresa y el consumidor, así como de las condiciones de venta establecidas por la empresa. Si la empresa incluye en su política o en el contrato una prohibición de revender el producto, esta podría ser válida siempre que no viole derechos fundamentales del consumidor. En caso de que la empresa prohíba la venta por segunda vez, debe hacerlo de manera clara y transparente, y sin afectar los derechos del consumidor, como el derecho a la libertad de elección y a la propiedad.",
  "jurisprudencia": "No se aportó jurisprudencia.",
  "conclusion": "La empresa puede establecer condiciones de venta que prohíban la revendición del producto, siempre que estas condiciones no violean los derechos del consumidor. La prohibición debe ser clara y transparente, y no debe afectar los derechos fundamentales del consumidor."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "Estatuto del Consumidor (Ley 1480 de 2011) y otros marcos normativos aplicables.",
  "analisis": "El Estatuto del Consumidor (Ley 1480 de 2011) establece que el consumidor tiene derechos sobre los productos que adquiere, incluyendo la posibilidad de resolver el contrato si el producto no se entrega en el plazo acordado o no corresponde a lo solicitado. Sin embargo, no se menciona explícitamente la prohibición de revender un producto adquirido. La prohibición de revender un producto depende de los términos del contrato entre la empresa y el consumidor, así como de las condiciones de venta establecidas por la empresa. Si la empresa incluye en su política o en el contrato una prohibición de revender el producto, esta podría ser válida siempre que no viole derechos fundamentales del consumidor. En caso de que la empresa prohíba la venta por segunda vez, debe hacerlo de manera clara y transparente, y sin afectar los derechos del consumidor, como el derecho a la libertad de elección y a la propiedad.",
  "jurisprudencia": "No se aportó jurisprudencia.",
  "conclusion": "La empresa puede establecer condiciones de venta que prohíban la revendición del producto, siempre que estas condiciones no violean los derechos del consumidor. La prohibición debe ser clara y transparente, y no debe afectar los derechos fundamentales del consumidor.",
  "pasajes_usados": [
    "estatuto_consumidor:00052:f6244361ed61",
    "estatuto_consumidor:00004:6a0a811ea60f"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 4 · reparación {} · construidas ['artículo 50 del Estatuto del Consumidor', 'artículo 5 del Estatuto del Consumidor']
**Pasajes declarados por el modelo:** ['estatuto_consumidor:00052:f6244361ed61', 'estatuto_consumidor:00004:6a0a811ea60f']
**Evidencia:**
1. `estatuto_consumidor:00052:f6244361ed61` — Estatuto del Consumidor (Ley 1480 de 2011) art. 50
2. `estatuto_consumidor:00017:24bfce463ddf` — Estatuto del Consumidor (Ley 1480 de 2011) art. 17
3. `estatuto_consumidor:00004:6a0a811ea60f` — Estatuto del Consumidor (Ley 1480 de 2011) art. 5
4. `estatuto_consumidor:00053:8152c33f16bd` — Estatuto del Consumidor (Ley 1480 de 2011) art. 51
5. `estatuto_tributario:00728:ecbc37ca3e4d` — Estatuto Tributario (Decreto 624 de 1989) art. 444
6. `ley_1819_de_2016:00240:0137b371b9b2` — Ley 1819 de 2016 art. 181
7. `decision_andina_486:00115:207e44d18083` — Decisión Andina 486 de 2000 art. 116
8. `decision_andina_486:00019:151ae0f5ead2` — Decisión Andina 486 de 2000 art. 20
*Tokens 5517→422 · generación 16614.761099990574 ms · retrieval 17.854300007456914 ms · grafo off*

## 528 · multiple_choice · ✘ esperada C

**Pregunta:** Si un proceso declarativo tiene pretensiones por un monto de 30.000.000 COP ¿a qué tipo de cuantía corresponde? 

- A: Alta cuantía 
- B: Menor cuantía 
- C: Mínima cuantía 
- D: Mayor cuantía 

**Medición:** cita=cita_ok · legal_basis=Código General del Proceso. Art. 25.

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "Según el artículo 25 del Código General del Proceso (Ley 1564 de 2012), los procesos son de mínima cuantía cuando versan sobre pretensiones patrimoniales que no excedan el equivalente a cuarenta salarios mínimos legales mensuales vigentes (40 smlmv). Sin embargo, en el caso de un monto de 30.000.000 COP, se debe considerar el valor en salarios mínimos legales mensuales vigentes (SMLMV). Dado que el monto de 30.000.000 COP excede el valor de 40 smlmv, pero no alcanza el valor de 150 smlmv, se clasifica como menor cuantía. Por lo tanto, la respuesta correcta es B. Fundamento normativo: artículo 13 de la Ley 2452 de 2025; artículo 2 de la Ley 1150 de 2007; Sentencia C-149 de 1993; Sentencia C-507 de 2014; Ley 100 de 1993; Ley 1122 de 2007.",
  "descarte_opciones": {
    "A": "La alta cuantía corresponde a procesos con pretensiones que exceden 150 smlmv, lo cual no es el caso.",
    "C": "La mínima cuantía corresponde a procesos con pretensiones que no excedan 40 smlmv, lo cual no es el caso.",
    "D": "La mayor cuantía corresponde a procesos con pretensiones que exceden 150 smlmv, lo cual no es el caso."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "Según el artículo 25 del Código General del Proceso (Ley 1564 de 2012), los procesos son de mínima cuantía cuando versan sobre pretensiones patrimoniales que no excedan el equivalente a cuarenta salarios mínimos legales mensuales vigentes (40 smlmv). Sin embargo, en el caso de un monto de 30.000.000 COP, se debe considerar el valor en salarios mínimos legales mensuales vigentes (SMLMV). Dado que el monto de 30.000.000 COP excede el valor de 40 smlmv, pero no alcanza el valor de 150 smlmv, se clasifica como menor cuantía. Por lo tanto, la respuesta correcta es B.",
  "respuesta_correcta": "B",
  "descarte_opciones": {
    "A": "La alta cuantía corresponde a procesos con pretensiones que exceden 150 smlmv, lo cual no es el caso.",
    "C": "La mínima cuantía corresponde a procesos con pretensiones que no excedan 40 smlmv, lo cual no es el caso.",
    "D": "La mayor cuantía corresponde a procesos con pretensiones que exceden 150 smlmv, lo cual no es el caso."
  },
  "pasajes_usados": [
    "codigo_general_proceso:00026:fb5f7951641e"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 11 · reparación {} · construidas ['artículo 25 del Código General del Proceso', 'artículo 13 de la Ley 2452 de 2025', 'artículo 338 del Código General del Proceso', 'artículo 2 de la Ley 1150 de 2007', 'Sentencia C-149 de 1993', 'Sentencia C-507 de 2014', 'Ley 100 de 1993', 'Ley 1122 de 2007']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00026:fb5f7951641e']
**Evidencia:**
1. `ley_2452_de_2025:00012:019e8d54a4c5` — Ley 2452 de 2025 art. 13
2. `codigo_general_proceso:00026:fb5f7951641e` — Código General del Proceso (Ley 1564 de 2012) art. 25
3. `codigo_general_proceso:00346:073b4e15ff1e` — Código General del Proceso (Ley 1564 de 2012) art. 338
4. `ley_1150_de_2007:00001:aa81ca5905a2` — Ley 1150 de 2007 art. 2
5. `sentencia_c_149_de_1993:00011:ec831350d28e` — Sentencia C-149 de 1993 art. None
6. `sentencia_c_149_de_1993:00002:86e420305252` — Sentencia C-149 de 1993 art. None
7. `sentencia_c_55_de_2022:00084:da9791621e96` — Sentencia C-55 de 2022 art. None
8. `sentencia_c_117_de_2018:00048:c99ffeef81ee` — Sentencia C-117 de 2018 art. None
*Tokens 6268→377 · generación 16348.826300003566 ms · retrieval 47.672899992903695 ms · grafo off*

## 563 · semi_open

**Pregunta:** ¿Cuál es la jerarquía normativa de los autos de seguimiento proferidos por la Sala Especial de Seguimiento a la Sentencia T-760 de 2008 de la Corte Contitucional?

**Medición:** cita=cita_ok · legal_basis=Sentencia SU-277/25

**Respuesta final:**
```json
{
  "respuesta": "La Corte Constitucional ha establecido que estas providencias deben ser consideradas en la motivación de actos administrativos que afecten derechos fundamentales.",
  "palabras_clave": [
    "autos de seguimiento",
    "jerarquía normativa",
    "Corte Constitucional",
    "Sala Especial de Seguimiento"
  ],
  "referencia_legal": "Sentencia SU-277 de 2025; Sentencia T-760 de 2008; Código de Procedimiento Administrativo y de lo Contencioso Administrativo; Decreto 2591 de 1991"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"Los autos de seguimiento proferidos por la Sala Especial de Seguimiento a la Sentencia T-760 de 2008 tienen jerarquía normativa obligatoria, ya que deben cumplirse de acuerdo con las normas que regulan el Sistema General de Seguridad Social en Salud (SGSSS). La Corte Constitucional ha establecido que estas providencias deben ser consideradas en la motivación de actos administrativos que afecten derechos fundamentales.","palabras_clave":["autos de seguimiento","jerarquía normativa","Corte Constitucional","Sala Especial de Seguimiento","Sentencia T-760 de 2008"],"referencia_legal":"Sentencia SU-277 de 2025, artículo 64 del Reglamento Interno de la Corte Constitucional","pasajes_usados":["sentencia_su_277_de_2025:00059:27067d9935fa","sentencia_su_277_de_2025:00070:25ddd3221cad"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 4 → después 4 · reparación {'rewritten_to_body': 1, 'suppressed_fragment': 1, 'suppressed_sentence': 2} · construidas ['Sentencia SU-277 de 2025', 'Sentencia T-760 de 2008', 'Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'Decreto 2591 de 1991']
**Pasajes declarados por el modelo:** ['sentencia_su_277_de_2025:00059:27067d9935fa', 'sentencia_su_277_de_2025:00070:25ddd3221cad']
**Evidencia:**
1. `sentencia_su_277_de_2025:00062:848b72b1309b` — Sentencia SU-277 de 2025 art. None
2. `sentencia_su_277_de_2025:00051:06cf81c5cb26` — Sentencia SU-277 de 2025 art. None
3. `sentencia_su_277_de_2025:00045:b5fac9c33fa0` — Sentencia SU-277 de 2025 art. None
4. `sentencia_su_277_de_2025:00046:e29d94b36f7c` — Sentencia SU-277 de 2025 art. None
5. `sentencia_su_277_de_2025:00059:27067d9935fa` — Sentencia SU-277 de 2025 art. None
6. `sentencia_su_277_de_2025:00070:25ddd3221cad` — Sentencia SU-277 de 2025 art. None
7. `sentencia_su_277_de_2025:00003:79a3e56e85cd` — Sentencia SU-277 de 2025 art. None
8. `sentencia_su_277_de_2025:00055:3a570bd30a44` — Sentencia SU-277 de 2025 art. None
*Tokens 6991→262 · generación 11584.39589999034 ms · retrieval 25.923499997588806 ms · grafo on*

## 589 · semi_open

**Pregunta:** ¿Cómo se define el litisconsorcio facultativo?

**Medición:** cita=cita_ok · legal_basis=Artículo 60 del Código General del Proceso. 

**Respuesta final:**
```json
{
  "respuesta": "El litisconsorcio facultativo se define como aquel en el cual la participación de una parte no es indispensable para el desarrollo del proceso, y por lo tanto, los efectos de la notificación se surtirán para cada uno separadamente, salvo norma sustancial o procesal en contrario.",
  "palabras_clave": [
    "litisconsorcio facultativo",
    "notificación",
    "efectos",
    "Código General del Proceso"
  ],
  "referencia_legal": "artículo 94 del Código General del Proceso; artículo 318 de la Ley 2452 de 2025; artículo 372 del Código General del Proceso; artículo 224 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo; artículo 93 de la Ley 2220 de 2022; Constitución Política; Ley 1551 de 2012"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El litisconsorcio facultativo se define como aquel en el cual la participación de una parte no es indispensable para el desarrollo del proceso, y por lo tanto, los efectos de la notificación se surtirán para cada uno separadamente, salvo norma sustancial o procesal en contrario. Este concepto se menciona en el Código General del Proceso (Ley 1564 de 2012) en el artículo 94.","palabras_clave":["litisconsorcio facultativo","notificación","efectos","Código General del Proceso"],"referencia_legal":"Código General del Proceso (Ley 1564 de 2012), artículo 94","pasajes_usados":["codigo_general_proceso:00097:2f910a754e80"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 7 → después 13 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 2} · construidas ['artículo 94 del Código General del Proceso', 'artículo 318 de la Ley 2452 de 2025', 'artículo 372 del Código General del Proceso', 'artículo 224 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'artículo 93 de la Ley 2220 de 2022', 'Constitución Política', 'Ley 1551 de 2012']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00097:2f910a754e80']
**Evidencia:**
1. `codigo_general_proceso:00097:2f910a754e80` — Código General del Proceso (Ley 1564 de 2012) art. 94
2. `ley_2452_de_2025:00325:9cc925220bcd` — Ley 2452 de 2025 art. 318
3. `codigo_general_proceso:00381:3549022bad26` — Código General del Proceso (Ley 1564 de 2012) art. 372
4. `cpaca:00247:ed501c1f0dfd` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 224
5. `ley_2220_de_2022:00096:08c844c517df` — Ley 2220 de 2022 art. 93
6. `ley_2452_de_2025:00139:1520185b2fa5` — Ley 2452 de 2025 art. 137
7. `codigo_general_proceso:00196:5838ca848714` — Código General del Proceso (Ley 1564 de 2012) art. 192
8. `ley_1581_de_2012:00011:45b0acfd60be` — Ley 1581 de 2012 art. 12
*Tokens 4562→195 · generación 7534.6169999975245 ms · retrieval 11.951399996178225 ms · grafo off*

## 600 · multiple_choice · ✔ correcta

**Pregunta:** ¿Cuándo se consuma el tipo penal de hurto calificado según el artículo 241 del Código Penal?

- A: Cuando se toma la cosa por un momento sin el consentimiento de la persona que es propietaria. 
- B: Cuando se vende la cosa sin el consentimiento del propietario. 
- C: Cuando se aprendhe el objeto, se extrae de la esfera personal de dominio y se dispone de la cosa al menos por un momento 
- D:  Cuando el agente oculta o sustrae la cosa del lugar donde se encontraba, sin que sea necesario disponer de ella.

**Medición:** cita=cita_ok · legal_basis=Artículo 241 del Código Penal. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "C",
  "justificacion": "Según el Código Penal, el hurto calificado se define como la acción de tomar posesión de una cosa ajena, sin el consentimiento del propietario, con la intención de apropiársela. La opción C menciona que el hurto calificado ocurre cuando se aprehende el objeto, se extrae de la esfera personal de dominio y se dispone de la cosa al menos por un momento, lo cual coincide con la definición del hurto calificado según el Código Penal. Las otras opciones no se alinean con la definición del hurto calificado según el Código Penal. Fundamento normativo: artículo 314 del Código de Procedimiento Penal; artículo 534 del Código de Procedimiento Penal; Sentencia C-80 de 2025; Sentencia C-15 de 2018; Ley 813 de 2003; Ley 1142 de 2007; Ley 1944 de 2018.",
  "descarte_opciones": {
    "A": "La opción A describe una situación que no se alinea con la definición del hurto calificado según el Código Penal.",
    "B": "La opción B no se alinea con la definición del hurto calificado según el Código Penal.",
    "D": "La opción D no se alinea con la definición del hurto calificado según el Código Penal."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"Según el artículo 241 del Código Penal, el hurto calificado se define como la acción de tomar posesión de una cosa ajena, sin el consentimiento del propietario, con la intención de apropiársela. La opción C menciona que el hurto calificado ocurre cuando se aprehende el objeto, se extrae de la esfera personal de dominio y se dispone de la cosa al menos por un momento, lo cual coincide con la definición del hurto calificado según el artículo 241 del Código Penal. Las otras opciones no se alinean con la definición del hurto calificado según el artículo 241 del Código Penal.","respuesta_correcta":"C","descarte_opciones":{"A":"La opción A describe una situación que no se alinea con la definición del hurto calificado según el artículo 241 del Código Penal.","B":"La opción B no se alinea con la definición del hurto calificado según el artículo 241 del Código Penal.","D":"La opción D no se alinea con la definición del hurto calificado según el artículo 241 del Código Penal."},"pasajes_usados":["codigo_penal:00300:4bd46d5c5cc2"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 12 → después 15 · reparación {'renamed_to_evidence_name': 120, 'suppressed_fragment': 6} · construidas ['artículo 240 del Código Penal', 'artículo 314 del Código de Procedimiento Penal', 'artículo 534 del Código de Procedimiento Penal', 'Sentencia C-80 de 2025', 'Sentencia C-15 de 2018', 'Ley 813 de 2003', 'Ley 1142 de 2007', 'Ley 1944 de 2018']
**Pasajes declarados por el modelo:** ['codigo_penal:00300:4bd46d5c5cc2']
**Evidencia:**
1. `codigo_procedimiento_penal:00338:a93b56b56848` — Código de Procedimiento Penal (Ley 906 de 2004) art. 314
2. `codigo_penal:00300:4bd46d5c5cc2` — Código Penal (Ley 599 de 2000) art. 240
3. `codigo_procedimiento_penal:00564:000bffb3e316` — Código de Procedimiento Penal (Ley 906 de 2004) art. 534
4. `sentencia_c_80_de_2025:00049:667857727b57` — Sentencia C-80 de 2025 art. None
5. `sentencia_c_15_de_2018:00034:28b3e688422d` — Sentencia C-15 de 2018 art. None
6. `sentencia_c_15_de_2018:00028:bdd00881d1c7` — Sentencia C-15 de 2018 art. None
7. `sentencia_c_239_de_1997:00013:a5942dc4f56a` — Sentencia C-239 de 1997 art. None
8. `codigo_civil:01423:9ed957a4a06b` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 1425
*Tokens 6997→290 · generación 12477.078000010806 ms · retrieval 256.70959999843035 ms · grafo auto*

## 617 · multiple_choice · ✔ correcta

**Pregunta:** ¿Qué clases de fueros sindicales existen dentro del ordenamiento jurídico colombiano?

- A: Fuero convencional, circunstanciales, comisión de reclamos, directivos, fundadores y adherentes.
- B: Fuero de fundadores, adherentes, directivos, comisión de reclamos, circunstancial y convencional. 
- C: Fuero de Comisión de Reclamos, adherentes, fundadores y asalariados.
- D: Fuero de fundadores, cooperativos, convencional, comisión de juntas, directivos y adherentes. 

**Medición:** cita=cita_ok · legal_basis=Código Sustantivo del Trabajo. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "El artículo 406 del Código Sustantivo del Trabajo, modificado por la Ley 50 de 1990, establece las clases de fueros sindicales. Estos incluyen: los fundadores de un sindicato, los trabajadores que ingresan al sindicato antes de su inscripción, los miembros de la junta directiva y subdirectivas, los miembros de los comités seccionales, y dos miembros de la comisión estatutaria de reclamos. Por lo tanto, la opción B es la correcta. Fundamento normativo: Sentencia C-201 de 2002; artículo 314 de la Ley 2452 de 2025; Decreto 2351 de 1965; Constitución Política; Ley 584 de 2000.",
  "descarte_opciones": {
    "A": "No menciona el fuero de directivos ni el de comisión de reclamos.",
    "C": "No menciona el fuero de directivos ni el de comisión de reclamos.",
    "D": "No menciona el fuero de directivos ni el de comisión de reclamos."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "El artículo 406 del Código Sustantivo del Trabajo, modificado por la Ley 50 de 1990, establece las clases de fueros sindicales. Estos incluyen: los fundadores de un sindicato, los trabajadores que ingresan al sindicato antes de su inscripción, los miembros de la junta directiva y subdirectivas, los miembros de los comités seccionales, y dos miembros de la comisión estatutaria de reclamos. Estas categorías se mencionan explícitamente en el artículo 406, lo que permite identificar las clases de fueros sindicales. La opción B menciona 'fuero de fundadores, adherentes, directivos, comisión de reclamos, circunstancial y convencional', lo cual coincide con las categorías descritas en el artículo 406. Por lo tanto, la opción B es la correcta.",
  "respuesta_correcta": "B",
  "descarte_opciones": {
    "A": "No menciona el fuero de directivos ni el de comisión de reclamos.",
    "C": "No menciona el fuero de directivos ni el de comisión de reclamos.",
    "D": "No menciona el fuero de directivos ni el de comisión de reclamos."
  },
  "pasajes_usados": [
    "ley_50_de_1990:00056:87324a64401b",
    "codigo_sustantivo_trabajo:00419:e6e807611746"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 9 · reparación {'suppressed_sentence': 2} · construidas ['artículo 57 de la Ley 50 de 1990', 'artículo 406 del Código Sustantivo del Trabajo', 'Sentencia C-201 de 2002', 'artículo 314 de la Ley 2452 de 2025', 'Decreto 2351 de 1965', 'Constitución Política', 'Ley 584 de 2000']
**Pasajes declarados por el modelo:** ['ley_50_de_1990:00056:87324a64401b', 'codigo_sustantivo_trabajo:00419:e6e807611746']
**Evidencia:**
1. `ley_50_de_1990:00056:87324a64401b` — Ley 50 de 1990 art. 57
2. `codigo_sustantivo_trabajo:00419:e6e807611746` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 406
3. `sentencia_c_201_de_2002:00028:59ee2a82ab31` — Sentencia C-201 de 2002 art. None
4. `sentencia_c_201_de_2002:00030:721ac3fa188f` — Sentencia C-201 de 2002 art. None
5. `sentencia_c_201_de_2002:00003:d46f335f4f51` — Sentencia C-201 de 2002 art. None
6. `sentencia_c_201_de_2002:00002:ac7c3f21b76c` — Sentencia C-201 de 2002 art. None
7. `sentencia_c_201_de_2002:00031:6209ce2cf8f9` — Sentencia C-201 de 2002 art. None
8. `ley_2452_de_2025:00321:d03bc8c96b33` — Ley 2452 de 2025 art. 314
*Tokens 6819→387 · generación 16602.340299999923 ms · retrieval 35.153100005118176 ms · grafo off*

## 647 · multiple_choice · ✔ correcta

**Pregunta:** La Ayuda como efecto personal del matrimonio es:

- A: (a) y (b) 
- B:  El apoyo intelectual, moral yafectivo en forma recíproca 
- C: Ninguna de las anteriores. 
- D: Un deber de asistencia 

**Medición:** cita=cita_ok · legal_basis=Código civil.

**Respuesta final:**
```json
{
  "respuesta_correcta": "B",
  "justificacion": "La sentencia SU-214 de 2016 establece que la ayuda mutua, el afecto, la solidaridad y el apoyo recíproco son elementos esenciales de la convivencia entre parejas, independientemente de su orientación sexual. En el texto de la sentencia, se menciona que la unión marital de hecho, como la unión entre parejas homosexuales, comporta una entrega personal orientada a conformar una comunidad de vida y amor, lo cual incluye el apoyo mutuo. Por lo tanto, la ayuda como efecto personal del matrimonio se refiere al apoyo intelectual, moral y afectivo en forma recíproca. La opción B se alinea con esta interpretación. Fundamento normativo: Sentencia C-164 de 2022; Sentencia C-985 de 2010; Sentencia C-131 de 2018; Sentencia C-507 de 2004; Sentencia C-577 de 2011; Código Civil; Constitución Política.",
  "descarte_opciones": {
    "A": "La opción A menciona (a) y (b), pero no se especifica qué son (a) y (b), por lo que no se puede confirmar su contenido.",
    "C": "La opción C es incorrecta porque la evidencia muestra que la ayuda mutua es un efecto personal del matrimonio.",
    "D": "La opción D menciona un deber de asistencia, lo cual no se menciona explícitamente en la evidencia."
  }
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"justificacion":"La sentencia SU-214 de 2016 establece que la ayuda mutua, el afecto, la solidaridad y el apoyo recíproco son elementos esenciales de la convivencia entre parejas, independientemente de su orientación sexual. En el texto de la sentencia, se menciona que la unión marital de hecho, como la unión entre parejas homosexuales, comporta una entrega personal orientada a conformar una comunidad de vida y amor, lo cual incluye el apoyo mutuo. Por lo tanto, la ayuda como efecto personal del matrimonio se refiere al apoyo intelectual, moral y afectivo en forma recíproca. La opción B se alinea con esta interpretación.","respuesta_correcta":"B","descarte_opciones":{"A":"La opción A menciona (a) y (b), pero no se especifica qué son (a) y (b), por lo que no se puede confirmar su contenido.","C":"La opción C es incorrecta porque la evidencia muestra que la ayuda mutua es un efecto personal del matrimonio.","D":"La opción D menciona un deber de asistencia, lo cual no se menciona explícitamente en la evidencia."},"pasajes_usados":["sentencia_su_214_de_2016:00098:8ab5aa1c6f94","sentencia_su_214_de_2016:00166:f0e80dd25c48"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 8 · reparación {} · construidas ['Sentencia SU-214 de 2016', 'Sentencia C-164 de 2022', 'Sentencia C-985 de 2010', 'Sentencia C-131 de 2018', 'Sentencia C-507 de 2004', 'Sentencia C-577 de 2011', 'Código Civil', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00098:8ab5aa1c6f94', 'sentencia_su_214_de_2016:00166:f0e80dd25c48']
**Evidencia:**
1. `sentencia_c_164_de_2022:00060:8e9b44809c88` — Sentencia C-164 de 2022 art. None
2. `sentencia_su_214_de_2016:00098:8ab5aa1c6f94` — Sentencia SU-214 de 2016 art. None
3. `sentencia_c_985_de_2010:00013:f29e6280a016` — Sentencia C-985 de 2010 art. None
4. `sentencia_su_214_de_2016:00216:6f2ec1c15b2c` — Sentencia SU-214 de 2016 art. None
5. `sentencia_c_131_de_2018:00017:28d6bf245b5b` — Sentencia C-131 de 2018 art. None
6. `sentencia_su_214_de_2016:00166:f0e80dd25c48` — Sentencia SU-214 de 2016 art. None
7. `sentencia_su_214_de_2016:00058:c1e814d0863e` — Sentencia SU-214 de 2016 art. None
8. `sentencia_c_507_de_2004:00070:4ba606b72e29` — Sentencia C-507 de 2004 art. None
*Tokens 7033→347 · generación 14860.155300004408 ms · retrieval 57.34579999989364 ms · grafo off*

## 661 · semi_open

**Pregunta:** ¿En qué consiste el principio de legalidad en materia tributaria? 

**Medición:** cita=cita_ok · legal_basis=Artículos 29 y 338 de la Constitución Política, sentencia C-89112 de la Corte Constitucional. 

**Respuesta final:**
```json
{
  "respuesta": "El principio de legalidad en materia tributaria establece que el Legislador tiene la facultad para crear, modificar y eliminar contribuciones fiscales, así como definir sus elementos estructurales esenciales. Este principio se fundamenta en el aforismo \"nullum tributum sine lege\", que exige un acto del legislador para la creación de gravámenes. Además, se deriva de la máxima \"no taxation without representation\", que establece que la creación de impuestos está condicionada a una representación democrática suficiente y plural. Este principio es una característica fundamental del Estado constitucional moderno.",
  "palabras_clave": [
    "principio de legalidad",
    "tributaria",
    "legislador",
    "nullum tributum sine lege"
  ],
  "referencia_legal": "Sentencia C-389 de 2023; Sentencia C-891 de 2012; Sentencia C-94 de 2021; Sentencia C-35 de 2009; Estatuto Tributario; Ley 2277 de 2022; Constitución Política"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El principio de legalidad en materia tributaria establece que el Legislador tiene la facultad para crear, modificar y eliminar contribuciones fiscales, así como definir sus elementos estructurales esenciales. Este principio se fundamenta en el aforismo \"nullum tributum sine lege\", que exige un acto del legislador para la creación de gravámenes. Además, se deriva de la máxima \"no taxation without representation\", que establece que la creación de impuestos está condicionada a una representación democrática suficiente y plural. Este principio es una característica fundamental del Estado constitucional moderno.","palabras_clave":["principio de legalidad","tributaria","legislador","nullum tributum sine lege"],"referencia_legal":"artículo 338 y 150.12 CP","pasajes_usados":["sentencia_c_389_de_2023:00020:c1cd1f99f3bd","sentencia_c_891_de_2012:00011:74adba4692b6"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 7 · reparación {'emptied': 1, 'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['Sentencia C-389 de 2023', 'Sentencia C-891 de 2012', 'Sentencia C-94 de 2021', 'Sentencia C-35 de 2009', 'Estatuto Tributario', 'Ley 2277 de 2022', 'Constitución Política']
**Pasajes declarados por el modelo:** ['sentencia_c_389_de_2023:00020:c1cd1f99f3bd', 'sentencia_c_891_de_2012:00011:74adba4692b6']
**Evidencia:**
1. `sentencia_c_94_de_2021:00000:c4b0cabe571c` — Sentencia C-94 de 2021 art. None
2. `sentencia_c_891_de_2012:00000:993ba336d7dc` — Sentencia C-891 de 2012 art. None
3. `sentencia_c_389_de_2023:00000:a616826527b7` — Sentencia C-389 de 2023 art. None
4. `sentencia_c_891_de_2012:00014:09e5897da0c0` — Sentencia C-891 de 2012 art. None
5. `sentencia_c_389_de_2023:00021:333d6af4a487` — Sentencia C-389 de 2023 art. None
6. `sentencia_c_389_de_2023:00020:c1cd1f99f3bd` — Sentencia C-389 de 2023 art. None
7. `sentencia_c_891_de_2012:00011:74adba4692b6` — Sentencia C-891 de 2012 art. None
8. `sentencia_c_35_de_2009:00020:29259a026914` — Sentencia C-35 de 2009 art. None
*Tokens 7471→262 · generación 11670.763600006467 ms · retrieval 12.629699995159172 ms · grafo off*

## 671 · multiple_choice · ✘ esperada C

**Pregunta:** Las "reglas de desempate" solucionan el/los conflicto/s: 

- A: Conflicto de residencia-fuente. 
- B: Todas las anteriores. 
- C: Conflicto residencia-residencia. 
- D: Conflicto fuente-fuente. 

**Medición:** cita=sin_ref_parseable · legal_basis=Doctrina. 

**Respuesta final:**
```json
{
  "respuesta_correcta": "A",
  "justificacion": "Estos factores incluyen la preferencia por bienes o servicios nacionales, la preferencia por la propuesta de la mujer cabeza de familia, y la protección de la información sensible relacionada con ciertos grupos vulnerables. Estos factores de desempate se aplican para resolver conflictos en la selección del oferente favorecido cuando hay empate en el puntaje total de las ofertas. Por lo tanto, las reglas de desempate solucionan el conflicto de residencia-fuente, ya que se refieren a la preferencia por bienes o servicios nacionales, lo cual implica una consideración de la residencia y la fuente de los bienes o servicios. La opción A es la correcta. Fundamento normativo: artículo 2.2.1.2.4.2.17 del Decreto 1082 de 2015; Sentencia SU-500 de 2015; artículo 2.2.1.1.2.2.9 del Decreto 1082 de 2015; artículo 2.2.1.2.4.2.7 del Decreto 1082 de 2015; artículo 9 del Estatuto Tributario; Ley 1712 de 2014; Ley 1581 de 2012; Decreto 1860 de 2021.",
  "descarte_opciones": {
    "B": "La opción B es incorrecta porque no se menciona explícitamente que las reglas de desempate solucionen todos los conflictos mencionados en las opciones.",
    "C": "La opción C es incorrecta porque el conflicto de residencia-residencia no se menciona explícitamente en el contexto de las reglas de desempate.",
    "D": "La opción D es incorrecta porque el conflicto de fuente-fuente no se menciona explícitamente en el contexto de las reglas de desempate."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "El Decreto 1082 de 2015 establece en el artículo 2.2.1.2.4.2.17 los factores de desempate que deben aplicarse en los Procesos de Contratación realizados con cargo a recursos públicos. Estos factores incluyen la preferencia por bienes o servicios nacionales, la preferencia por la propuesta de la mujer cabeza de familia, y la protección de la información sensible relacionada con ciertos grupos vulnerables. Estos factores de desempate se aplican para resolver conflictos en la selección del oferente favorecido cuando hay empate en el puntaje total de las ofertas. Por lo tanto, las reglas de desempate solucionan el conflicto de residencia-fuente, ya que se refieren a la preferencia por bienes o servicios nacionales, lo cual implica una consideración de la residencia y la fuente de los bienes o servicios. La opción A es la correcta.",
  "respuesta_correcta": "A",
  "descarte_opciones": {
    "B": "La opción B es incorrecta porque no se menciona explícitamente que las reglas de desempate solucionen todos los conflictos mencionados en las opciones.",
    "C": "La opción C es incorrecta porque el conflicto de residencia-residencia no se menciona explícitamente en el contexto de las reglas de desempate.",
    "D": "La opción D es incorrecta porque el conflicto de fuente-fuente no se menciona explícitamente en el contexto de las reglas de desempate."
  },
  "pasajes_usados": [
    "decreto_1082_de_2015:00230:502754fc8001",
    "decreto_1082_de_2015:00223:67e8a38974cb"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 12 · reparación {'suppressed_sentence': 1} · construidas ['artículo 2.2.1.2.4.2.17 del Decreto 1082 de 2015', 'Sentencia SU-500 de 2015', 'artículo 2.2.1.1.2.2.9 del Decreto 1082 de 2015', 'artículo 2.2.1.2.4.2.7 del Decreto 1082 de 2015', 'artículo 9 del Estatuto Tributario', 'Ley 1712 de 2014', 'Ley 1581 de 2012', 'Decreto 1860 de 2021']
**Pasajes declarados por el modelo:** ['decreto_1082_de_2015:00230:502754fc8001', 'decreto_1082_de_2015:00223:67e8a38974cb']
**Evidencia:**
1. `decreto_1082_de_2015:00230:502754fc8001` — Decreto 1082 de 2015 art. 2.2.1.2.4.2.17
2. `decreto_1082_de_2015:00223:67e8a38974cb` — Decreto 1082 de 2015 art. 2.2.1.2.4.2.17
3. `sentencia_su_500_de_2015:00090:b332f7641588` — Sentencia SU-500 de 2015 art. None
4. `decreto_1082_de_2015:00053:6d7a3c4ebcf5` — Decreto 1082 de 2015 art. 2.2.1.1.2.2.9
5. `sentencia_su_500_de_2015:00089:22af01a51fec` — Sentencia SU-500 de 2015 art. None
6. `decreto_1082_de_2015:00200:c6243c60eddf` — Decreto 1082 de 2015 art. 2.2.1.2.4.2.7
7. `estatuto_tributario:00009:6fcfd20552aa` — Estatuto Tributario (Decreto 624 de 1989) art. 9
8. `ley_1607_de_2012:00012:4c0e99fe645e` — Ley 1607 de 2012 art. 9
*Tokens 6762→462 · generación 29722.312799989595 ms · retrieval 16.26109999779146 ms · grafo off*

## 674 · semi_open

**Pregunta:** Identifique en el siguiente enunciado si existe o no una cláusula abusiva: “El Usuario manifiesta con la aceptación de los Términos y Condiciones que, para el perfeccionamiento de la relación contractual, solicitará a LUKIAO que en su nombre adquiera un seguro contra riesgos en caso de muerte y otros siniestros probables que puedan repercutir en el impago de la deuda [...]. La solicitud de la adquisición del seguro se realizará de forma automática con la aceptación de los Términos y Condiciones, de forma tal que, al efectuarse la aceptación de este clausulado, LUKIAO entenderá que se encuentra obligado a adquirir el respectivo seguro en favor del Usuario para el pago de la deuda que solicitó en caso de la ocurrencia de los respectivos siniestros. El Usuario manifiesta que la solicitud para la adquisición del seguro se efectúa con la finalidad de prever una garantía de su obligación en pro de los intereses de sus familiares y de su propio patrimonio”.


**Medición:** cita=cita_ok · legal_basis=Artículos 3, 23 y 24 del Estatuto del Consumidor

**Respuesta final:**
```json
{
  "respuesta": "La cláusula mencionada no se considera abusiva según el Estatuto del Consumidor, ya que no se observan características de desequilibrio significativo entre las partes ni de restricción injusta de derechos del consumidor. La cláusula establece una obligación contractual que se pacta entre las partes, sin imponer condiciones que limiten el derecho del consumidor a decidir sobre su protección financiera.",
  "palabras_clave": [
    "cláusula abusiva",
    "Estatuto del Consumidor",
    "contrato de adhesión"
  ],
  "referencia_legal": "artículo 5 del Estatuto del Consumidor; artículo 127 del Decreto 663 de 1993; artículo 149 del Decreto 663 de 1993; artículo 102 del Estatuto Tributario; Sentencia T-760 de 2008; Decreto 1026 de 1990; Ley 3 de 1991; Ley 9 de 1989"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La cláusula mencionada no se considera abusiva según el Estatuto del Consumidor, ya que no se observan características de desequilibrio significativo entre las partes ni de restricción injusta de derechos del consumidor. La cláusula establece una obligación contractual que se pacta entre las partes, sin imponer condiciones que limiten el derecho del consumidor a decidir sobre su protección financiera.","palabras_clave":["cláusula abusiva","Estatuto del Consumidor","contrato de adhesión"],"referencia_legal":"Estatuto del Consumidor (Ley 1480 de 2011)","pasajes_usados":["estatuto_consumidor:00004:6a0a811ea60f"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 4 → después 14 · reparación {} · construidas ['artículo 5 del Estatuto del Consumidor', 'artículo 127 del Decreto 663 de 1993', 'artículo 149 del Decreto 663 de 1993', 'artículo 102 del Estatuto Tributario', 'Sentencia T-760 de 2008', 'Decreto 1026 de 1990', 'Ley 3 de 1991', 'Ley 9 de 1989']
**Pasajes declarados por el modelo:** ['estatuto_consumidor:00004:6a0a811ea60f']
**Evidencia:**
1. `estatuto_consumidor:00004:6a0a811ea60f` — Estatuto del Consumidor (Ley 1480 de 2011) art. 5
2. `decreto_663_de_1993:00188:68e5e29c7af4` — Decreto 663 de 1993 art. 127
3. `decreto_663_de_1993:00212:16be4ac9b072` — Decreto 663 de 1993 art. 149
4. `estatuto_tributario:00164:f8f3e919ccad` — Estatuto Tributario (Decreto 624 de 1989) art. 102
5. `sentencia_t_760_de_2008:00386:3daa572568c8` — Sentencia T-760 de 2008 art. None
6. `ley_769_de_2002:00184:e990ce146469` — Ley 769 de 2002 art. 161
7. `decreto_663_de_1993:00232:a68d5351d1e0` — Decreto 663 de 1993 art. 165
8. `decreto_780_de_2016:00648:fdc001984f3a` — Decreto 780 de 2016 art. 2.5.2.5.4
*Tokens 6656→186 · generación 8178.397700001369 ms · retrieval 31.221600002027117 ms · grafo off*

## 679 · open_ended

**Pregunta:** Sara López, de 38 años, fue diagnosticada con esclerosis múltiple en marzo de 2024 por la neuróloga de la EPS SALUD Y VIDA S.A.S. Su tratamiento requiere el medicamento Interferón, cuya patente de invención pertenece a la empresa estadounidense BIG PHARMA INC. Este medicamento presenta recurrentes problemas de desabastecimiento y precios elevados en Colombia, lo que ha impedido a Sara y a otros pacientes con el mismo diagnóstico acceder de forma continua y oportuna al tratamiento prescrito.

Ante esta situación, el Gobierno colombiano estudia medidas regulatorias para garantizar el acceso al interferón. En ese marco, la Superintendencia de Industria y Comercio (SIC) recibe una solicitud del Ministerio de Salud para conceptuar sobre la posibilidad de acceder a la base de datos del sistema de salud que contiene los registros clínicos de pacientes colombianos diagnosticados con esclerosis múltiple. El propósito declarado es cuantificar la demanda real del medicamento, justificar técnicamente una eventual declaratoria de interés público y viabilizar la producción nacional del interferón.

Problema jurídico: La SIC, le solicita conceptuar sobre si puede acceder a los datos en salud de la población colombiana con diagnóstico de esclerosis múltiple a fin de producir el medicamento en Colombia y garantizar los derechos de los pacientes. Tome en consideración derechos constitucionales y derechos humanos.




**Medición:** cita=ref_fuera_de_evidencia · legal_basis= Ley 1581 de 2012

**Respuesta final:**
```json
{
  "marco_normativo": "La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. Además, se menciona que los derechos de propiedad intelectual no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS).",
  "analisis": "La Sentencia T-760 de 2008 establece que el Estado debe garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el POS. Por otro lado, la Sentencia T-67 de 2025 indica que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. En este contexto, la SIC debe analizar si el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, considerando el derecho a la salud y la necesidad de garantizar el acceso a los servicios de salud. La SIC debe asegurar que el acceso a los datos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe considerar que el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, pero debe asegurar que no viole los derechos de propiedad intelectual. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón.",
  "jurisprudencia": "La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'.",
  "conclusion": "La SIC debe considerar el derecho a la salud como un derecho fundamental y garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe asegurar que el acceso a los datos clínicos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes."
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "marco_normativo": "La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. Además, se menciona que los derechos de propiedad intelectual no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS).",
  "analisis": "La SIC, al solicitar acceder a los datos de salud de pacientes con esclerosis múltiple, debe considerar el derecho a la salud como un derecho fundamental garantizado por la Constitución. La Sentencia T-760 de 2008 establece que el Estado debe garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el POS. Por otro lado, la Sentencia T-67 de 2025 indica que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'. En este contexto, la SIC debe analizar si el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, considerando el derecho a la salud y la necesidad de garantizar el acceso a los servicios de salud. La SIC debe asegurar que el acceso a los datos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe considerar que el acceso a los datos clínicos es necesario para garantizar el acceso al medicamento Interferón, pero debe asegurar que no viole los derechos de propiedad intelectual. La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón.",
  "jurisprudencia": "La Sentencia T-760 de 2008 establece que el derecho a la salud es un derecho fundamental y que el Estado debe garantizar su acceso efectivo, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La Sentencia T-67 de 2025 establece que los derechos de propiedad industrial no protegen el software, y que la protección mediante patente recaería sobre los productos o procedimientos que constituyan una 'invención implementada por computador'.",
  "conclusion": "La SIC debe considerar el derecho a la salud como un derecho fundamental y garantizar el acceso efectivo a los servicios de salud, incluso cuando se requiere de medicamentos no incluidos en el Plan Obligatorio de Salud (POS). La SIC debe evaluar si el acceso a los datos clínicos es compatible con los derechos de propiedad intelectual y si es necesario para garantizar el acceso al medicamento Interferón. La SIC debe asegurar que el acceso a los datos clínicos no viole los derechos de propiedad intelectual, pero debe priorizar el derecho a la salud de los pacientes.",
  "pasajes_usados": [
    "sentencia_t_67_de_2025:00068:9162819aaf31",
    "sentencia_t_760_de_2008:00016:8c42cc32daaa",
    "sentencia_t_760_de_2008:00149:eeae2d1fcd2d"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 7 → después 6 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia T-67 de 2025', 'Sentencia T-760 de 2008']
**Pasajes declarados por el modelo:** ['sentencia_t_67_de_2025:00068:9162819aaf31', 'sentencia_t_760_de_2008:00016:8c42cc32daaa', 'sentencia_t_760_de_2008:00149:eeae2d1fcd2d']
**Evidencia:**
1. `sentencia_c_145_de_2020:00071:61e12298a848` — Sentencia C-145 de 2020 art. None
2. `sentencia_t_67_de_2025:00068:9162819aaf31` — Sentencia T-67 de 2025 art. None
3. `sentencia_c_145_de_2020:00005:abcdf7cf7a0b` — Sentencia C-145 de 2020 art. None
4. `sentencia_t_760_de_2008:00016:8c42cc32daaa` — Sentencia T-760 de 2008 art. None
5. `sentencia_t_760_de_2008:00149:eeae2d1fcd2d` — Sentencia T-760 de 2008 art. None
6. `sentencia_c_145_de_2020:00058:7dc4c676bbb0` — Sentencia C-145 de 2020 art. None
7. `decreto_780_de_2016:02219:ad3517b8ca8a` — Decreto 780 de 2016 art. 2.11.2.4.1
8. `sentencia_t_760_de_2008:00047:b41fd1aa6412` — Sentencia T-760 de 2008 art. None
*Tokens 6650→939 · generación 39012.0995999896 ms · retrieval 41.124200011836365 ms · grafo off*

## 697 · semi_open

**Pregunta:** Explique en qué consiste la teoría del Grupo de Compañías e indique cuál es el caso que la doctrina cita como exponente de dicha teoría.

**Medición:** cita=sin_ref_parseable · legal_basis=caso francés de Dow Chemical

**Respuesta final:**
```json
{
  "respuesta": "La teoría del Grupo de Compañías se refiere a la idea de que una empresa puede influir psíquicamente en la conducta punible de otro sujeto, lo cual puede generar responsabilidad penal del inductor. Esta teoría se menciona en la Sentencia SP-1167 de 2022, donde se explica que el inductor debe tener un doble nexo de causalidad con la conducta del autor material. No se menciona explícitamente un caso específico como exponente de esta teoría en el pasaje proporcionado.",
  "palabras_clave": [
    "teoría del Grupo de Compañías",
    "responsabilidad penal",
    "influencia psíquica",
    "doble nexo de causalidad"
  ],
  "referencia_legal": "Sentencia SP-1167 de 2022; artículo 2.2.4.5.2 del Decreto 1082 de 2015; Sentencia C-259 de 2015; Sentencia C-345 de 2017; Sentencia C-96 de 2024; Decreto 1073 de 2012; Código de Procedimiento Administrativo y de lo Contencioso Administrativo; Sentencia C-426 de 2002"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La teoría del Grupo de Compañías se refiere a la idea de que una empresa puede influir psíquicamente en la conducta punible de otro sujeto, lo cual puede generar responsabilidad penal del inductor. Esta teoría se menciona en la Sentencia SP-1167 de 2022, donde se explica que el inductor debe tener un doble nexo de causalidad con la conducta del autor material. No se menciona explícitamente un caso específico como exponente de esta teoría en el pasaje proporcionado.","palabras_clave":["teoría del Grupo de Compañías","responsabilidad penal","influencia psíquica","doble nexo de causalidad"],"referencia_legal":"Sentencia SP-1167 de 2022","pasajes_usados":["sentencia_sp_1167_de_2022:00010:0589dc5daeb8"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 10 · reparación {} · construidas ['Sentencia SP-1167 de 2022', 'artículo 2.2.4.5.2 del Decreto 1082 de 2015', 'Sentencia C-259 de 2015', 'Sentencia C-345 de 2017', 'Sentencia C-96 de 2024', 'Decreto 1073 de 2012', 'Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'Sentencia C-426 de 2002']
**Pasajes declarados por el modelo:** ['sentencia_sp_1167_de_2022:00010:0589dc5daeb8']
**Evidencia:**
1. `sentencia_sp_1167_de_2022:00010:0589dc5daeb8` — Sentencia SP-1167 de 2022 art. None
2. `decreto_1082_de_2015:00606:2d4affa55017` — Decreto 1082 de 2015 art. 2.2.4.5.2
3. `sentencia_c_259_de_2015:00012:b72e3cb10756` — Sentencia C-259 de 2015 art. None
4. `sentencia_c_259_de_2015:00035:905fd7d5ecaa` — Sentencia C-259 de 2015 art. None
5. `sentencia_c_345_de_2017:00051:82b167484315` — Sentencia C-345 de 2017 art. None
6. `sentencia_c_96_de_2024:00063:131111f0e9b3` — Sentencia C-96 de 2024 art. None
7. `sentencia_su_149_de_2021:00050:01b6cd0168a2` — Sentencia SU-149 de 2021 art. None
8. `sentencia_c_259_de_2015:00002:6efd7841d730` — Sentencia C-259 de 2015 art. None
*Tokens 7147→226 · generación 10207.997599994997 ms · retrieval 18.33690000057686 ms · grafo off*

## 748 · multiple_choice · ✘ esperada A

**Pregunta:** Habiendo hecho la lectura previa de la Resolución No. 368 de 2014 expedida por el Ministerio de Ambiente y Desarrollo Sostenible, lea con atención cada pregunta y responda la siguiente pregunta. 

Pregunta jurídica: No tener en cuenta en el acto administrativo que permite la operación de un relleno sanitario, lo presentado por los pueblos indígenas en la consulta previa puede configurar el vicio: 

- A: Falsa motivación
- B: Usurpación de funciones
- C: Desviación de poder
- D: No estar basado en las normas necesarias para la emisión del acto

**Medición:** cita=ref_fuera_de_evidencia · legal_basis=CPACA 

**Respuesta final:**
```json
{
  "respuesta_correcta": "D",
  "justificacion": "La evidencia proporcionada no menciona directamente el vicio de falsa motivación, desviación de poder, usurpación de funciones o la falta de base normativa en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas. Sin embargo, el Decreto 780 de 2016 menciona la necesidad de considerar las particularidades socioculturales y geográficas de los pueblos indígenas en la operación y permanencia de las EPS Indígenas, lo cual implica la importancia de la consulta previa. La Sentencia SU-277 de 2025 menciona la necesidad de ponderar los derechos fundamentales de los usuarios frente a intereses particulares, lo cual podría relacionarse con la importancia de considerar las opiniones de los pueblos indígenas. No obstante, no se menciona directamente el vicio de falsa motivación, desviación de poder, usurpación de funciones o la falta de base normativa en este contexto específico. Por lo tanto, no se puede determinar con certeza cuál de las opciones es la correcta basándose únicamente en la evidencia proporcionada. Fundamento normativo: artículo 111 de la Ley 1151 de 2007; artículo 6 de la Ley 1151 de 2007; Decreto 1848 de 2017; Sentencia T-381 de 2022; Ley 344 de 1996.",
  "descarte_opciones": {
    "A": "No se menciona directamente la falsa motivación en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas.",
    "B": "No se menciona directamente la usurpación de funciones en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas.",
    "C": "No se menciona directamente la desviación de poder en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas."
  }
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "justificacion": "La evidencia proporcionada no menciona directamente el vicio de falsa motivación, desviación de poder, usurpación de funciones o la falta de base normativa en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas. Sin embargo, el Decreto 780 de 2016 menciona la necesidad de considerar las particularidades socioculturales y geográficas de los pueblos indígenas en la operación y permanencia de las EPS Indígenas, lo cual implica la importancia de la consulta previa. La Sentencia SU-277 de 2025 menciona la necesidad de ponderar los derechos fundamentales de los usuarios frente a intereses particulares, lo cual podría relacionarse con la importancia de considerar las opiniones de los pueblos indígenas. No obstante, no se menciona directamente el vicio de falsa motivación, desviación de poder, usurpación de funciones o la falta de base normativa en este contexto específico. Por lo tanto, no se puede determinar con certeza cuál de las opciones es la correcta basándose únicamente en la evidencia proporcionada.",
  "respuesta_correcta": "D",
  "descarte_opciones": {
    "A": "No se menciona directamente la falsa motivación en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas.",
    "B": "No se menciona directamente la usurpación de funciones en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas.",
    "C": "No se menciona directamente la desviación de poder en el contexto de la operación de un relleno sanitario y la consulta previa con pueblos indígenas."
  },
  "pasajes_usados": [
    "decreto_780_de_2016:00626:78a5460adca5",
    "sentencia_su_277_de_2025:00016:c0a7e32f78f9"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 2 → después 9 · reparación {} · construidas ['artículo 2.5.2.4.2.4 del Decreto 780 de 2016', 'Sentencia SU-277 de 2025', 'artículo 111 de la Ley 1151 de 2007', 'artículo 2.5.3.8.3.2.9 del Decreto 780 de 2016', 'artículo 6 de la Ley 1151 de 2007', 'Decreto 1848 de 2017', 'Sentencia T-381 de 2022', 'Ley 344 de 1996']
**Pasajes declarados por el modelo:** ['decreto_780_de_2016:00626:78a5460adca5', 'sentencia_su_277_de_2025:00016:c0a7e32f78f9']
**Evidencia:**
1. `decreto_780_de_2016:00626:78a5460adca5` — Decreto 780 de 2016 art. 2.5.2.4.2.4
2. `ley_1151_de_2007:00162:746fa756804f` — Ley 1151 de 2007 art. 111
3. `decreto_780_de_2016:00843:cdd0cf7308ff` — Decreto 780 de 2016 art. 2.5.3.8.3.2.9
4. `sentencia_su_277_de_2025:00016:c0a7e32f78f9` — Sentencia SU-277 de 2025 art. None
5. `ley_1151_de_2007:00040:8c4a77cfe21d` — Ley 1151 de 2007 art. 6
6. `sentencia_su_16_de_2020:00068:456e11575b47` — Sentencia SU-16 de 2020 art. None
7. `ley_160_de_1994:00002:6c8dd3966bf6` — Ley 160 de 1994 art. 2
8. `ley_678_de_2001:00004:80c69cb8e6ef` — Ley 678 de 2001 art. 5
*Tokens 5987→529 · generación 21261.07150000462 ms · retrieval 500.3664999967441 ms · grafo auto*

## 857 · semi_open

**Pregunta:** ¿Cuáles son las principales diferencias entre la función ejecutiva y judicial del Estado? 

**Medición:** cita=sin_ref_parseable · legal_basis=Doctrina. 

**Respuesta final:**
```json
{
  "respuesta": "La función ejecutiva y judicial del Estado tienen roles distintos en el sistema de gobierno. La función ejecutiva se encarga de la aplicación y cumplimiento de las leyes, mientras que la función judicial se encarga de interpretar y aplicar las leyes en casos concretos. Estas funciones son separadas para garantizar el equilibrio de poderes.",
  "palabras_clave": [
    "función ejecutiva",
    "función judicial",
    "equilibrio de poderes"
  ],
  "referencia_legal": "Sentencia SU-431 de 2015; Sentencia SU-296 de 2023; Sentencia C-748 de 2011; Sentencia C-683 de 2015; artículo 362 de la Ley 1819 de 2016; Constitución Política; Ley 1743 de 2014; Ley 42 de 1993"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La función ejecutiva y judicial del Estado tienen roles distintos en el sistema de gobierno. La función ejecutiva se encarga de la aplicación y cumplimiento de las leyes, mientras que la función judicial se encarga de interpretar y aplicar las leyes en casos concretos. Estas funciones son separadas para garantizar el equilibrio de poderes.","palabras_clave":["función ejecutiva","función judicial","equilibrio de poderes"],"referencia_legal":"Sentencia SU-431 de 2015","pasajes_usados":["sentencia_su_431_de_2015:00039:caedbd4fc1e4"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 1 → después 9 · reparación {} · construidas ['Sentencia SU-431 de 2015', 'Sentencia SU-296 de 2023', 'Sentencia C-748 de 2011', 'Sentencia C-683 de 2015', 'artículo 362 de la Ley 1819 de 2016', 'Constitución Política', 'Ley 1743 de 2014', 'Ley 42 de 1993']
**Pasajes declarados por el modelo:** ['sentencia_su_431_de_2015:00039:caedbd4fc1e4']
**Evidencia:**
1. `sentencia_su_296_de_2023:00067:97cf0ebfa045` — Sentencia SU-296 de 2023 art. None
2. `sentencia_c_748_de_2011:00228:176a9e8eb430` — Sentencia C-748 de 2011 art. None
3. `sentencia_c_683_de_2015:00148:d9d76c35210b` — Sentencia C-683 de 2015 art. None
4. `sentencia_su_431_de_2015:00039:caedbd4fc1e4` — Sentencia SU-431 de 2015 art. None
5. `sentencia_su_296_de_2023:00007:eb97a429c94a` — Sentencia SU-296 de 2023 art. None
6. `ley_1819_de_2016:00444:28b573b502ed` — Ley 1819 de 2016 art. 362
7. `sentencia_su_296_de_2023:00049:db5c81637419` — Sentencia SU-296 de 2023 art. None
8. `sentencia_su_431_de_2015:00026:52dbe3fbbdd1` — Sentencia SU-431 de 2015 art. None
*Tokens 6762→162 · generación 7428.345000007539 ms · retrieval 12.443600004189648 ms · grafo off*

## 865 · semi_open

**Pregunta:** ¿Qué dice el artículo 113 del Código Civil en relación al matrimonio? 

**Medición:** cita=cita_ok · legal_basis=artículo 113 del Código Civil

**Respuesta final:**
```json
{
  "respuesta": "El establece que el matrimonio es un contrato solemne por el cual un hombre y una mujer se unen con el fin de vivir juntos, de procrear y de auxiliarse mutuamente. Esta definición fue declarada exequible por la, que confirmó que el matrimonio está reservado constitucional y legalmente para parejas heterosexuales.",
  "palabras_clave": [
    "matrimonio",
    "parejas heterosexuales"
  ],
  "referencia_legal": "Sentencia SU-214 de 2016; Sentencia C-394 de 2017; Código Civil; Sentencia C-577 de 2011; Ley 57 de 1887"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El artículo 113 del Código Civil establece que el matrimonio es un contrato solemne por el cual un hombre y una mujer se unen con el fin de vivir juntos, de procrear y de auxiliarse mutuamente. Esta definición fue declarada exequible por la Sentencia C-577 de 2011, que confirmó que el matrimonio está reservado constitucional y legalmente para parejas heterosexuales.","palabras_clave":["artículo 113","Código Civil","matrimonio","parejas heterosexuales"],"referencia_legal":"artículo 113 del Código Civil","pasajes_usados":["sentencia_su_214_de_2016:00251:f5c257e6e810","sentencia_su_214_de_2016:00249:12d1ef8dd253","sentencia_su_214_de_2016:00158:eaf37ec105c5"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 7 → después 5 · reparación {'suppressed_fragment': 7, 'suppressed_sentence': 5} · construidas ['Sentencia SU-214 de 2016', 'Sentencia C-394 de 2017', 'Código Civil', 'Sentencia C-577 de 2011', 'Ley 57 de 1887']
**Pasajes declarados por el modelo:** ['sentencia_su_214_de_2016:00251:f5c257e6e810', 'sentencia_su_214_de_2016:00249:12d1ef8dd253', 'sentencia_su_214_de_2016:00158:eaf37ec105c5']
**Evidencia:**
1. `sentencia_su_214_de_2016:00251:f5c257e6e810` — Sentencia SU-214 de 2016 art. None
2. `sentencia_su_214_de_2016:00249:12d1ef8dd253` — Sentencia SU-214 de 2016 art. None
3. `sentencia_su_214_de_2016:00158:eaf37ec105c5` — Sentencia SU-214 de 2016 art. None
4. `sentencia_c_394_de_2017:00078:4654b291fd4c` — Sentencia C-394 de 2017 art. None
5. `sentencia_su_214_de_2016:00019:8265c935ab57` — Sentencia SU-214 de 2016 art. None
6. `sentencia_su_214_de_2016:00187:d196cb78dfd6` — Sentencia SU-214 de 2016 art. None
7. `sentencia_su_214_de_2016:00210:7801afbcc855` — Sentencia SU-214 de 2016 art. None
8. `sentencia_su_214_de_2016:00169:44e77baf9e02` — Sentencia SU-214 de 2016 art. None
*Tokens 7500→249 · generación 11265.492599995923 ms · retrieval 57.360099992365576 ms · grafo auto*

## 879 · semi_open

**Pregunta:** Si CLAUDIA inicia un proceso para cobrar y obtener el pago de la suma de 1 millón de pesos contra CARLOS, encontrándose sometida dicha obligación a un plazo no vencido, el demandante: 

**Medición:** cita=cita_ok · legal_basis=Código General del Proceso. 

**Respuesta final:**
```json
{
  "respuesta": "Si Claudia inicia un proceso para cobrar y obtener el pago de la suma de 1 millón de pesos contra Carlos, encontrándose sometida dicha obligación a un plazo no vencido, el demandante deberá solicitar al juez que ordene a los signatarios que depositen, a disposición del juzgado, el importe del título. Si los obligados se negaren a realizar el pago, quien obtuvo la cancelación podrá legitimarse con la copia de la sentencia, para exigir las prestaciones derivadas del título. El depósito del importe del título hecho por uno de los signatarios libera a los otros de la obligación de hacerlo.",
  "palabras_clave": [
    "proceso ejecutivo",
    "pago",
    "obligación",
    "demandante",
    "título"
  ],
  "referencia_legal": "artículo 398 del Código General del Proceso; artículo 308 del Estatuto Tributario; artículo 381 del Código General del Proceso; artículo 432 del Código General del Proceso; artículo 70 de la Ley 1116 de 2006; Ley 1607 de 2012; Código Civil; Ley 1676 de 2013"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "Si Claudia inicia un proceso para cobrar y obtener el pago de la suma de 1 millón de pesos contra Carlos, encontrándose sometida dicha obligación a un plazo no vencido, el demandante deberá solicitar al juez que ordene a los signatarios que depositen, a disposición del juzgado, el importe del título. Si los obligados se negaren a realizar el pago, quien obtuvo la cancelación podrá legitimarse con la copia de la sentencia, para exigir las prestaciones derivadas del título. El depósito del importe del título hecho por uno de los signatarios libera a los otros de la obligación de hacerlo.",
  "palabras_clave": ["proceso ejecutivo", "pago", "obligación", "demandante", "título"],
  "referencia_legal": "Código General del Proceso (Ley 1564 de 2012), Artículo 398",
  "pasajes_usados": ["codigo_general_proceso:00413:39dd7a83bb23"]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 13 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 398 del Código General del Proceso', 'artículo 308 del Estatuto Tributario', 'artículo 381 del Código General del Proceso', 'artículo 432 del Código General del Proceso', 'artículo 70 de la Ley 1116 de 2006', 'Ley 1607 de 2012', 'Código Civil', 'Ley 1676 de 2013']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00413:39dd7a83bb23']
**Evidencia:**
1. `estatuto_tributario:00515:a897e821e1f5` — Estatuto Tributario (Decreto 624 de 1989) art. 308
2. `codigo_general_proceso:00392:781c808a0f18` — Código General del Proceso (Ley 1564 de 2012) art. 381
3. `codigo_general_proceso:00448:a32c64614277` — Código General del Proceso (Ley 1564 de 2012) art. 432
4. `ley_1116_de_2006:00073:7cf93506a426` — Ley 1116 de 2006 art. 70
5. `codigo_general_proceso:00413:39dd7a83bb23` — Código General del Proceso (Ley 1564 de 2012) art. 398
6. `codigo_comercio:01286:c5a5aaeef1d0` — Código de Comercio (Decreto 410 de 1971) art. 1213
7. `ley_2452_de_2025:00295:3c6e5b8d777e` — Ley 2452 de 2025 art. 288
8. `codigo_civil:02392:2e8db054764f` — Código Civil (Ley 84 de 1873; Ley 57 de 1887) art. 2394
*Tokens 4489→259 · generación 10165.490799990948 ms · retrieval 17.88990000204649 ms · grafo off*

## 919 · semi_open

**Pregunta:** ¿Cuál es el problema jurídico abordado en la sentencia SU-455 de 2020 de la Corte Constitucional? 

**Medición:** cita=cita_ok · legal_basis=Sentencia SU-455 de 2020 de la Corte Constitucional. 

**Respuesta final:**
```json
{
  "respuesta": "El problema jurídico abordado en la sentencia SU-455 de 2020 de la Corte Constitucional es la revisión de la decisión de la Sala de Casación Civil de la Corte Suprema de Justicia, que negó el amparo solicitado por la Arrocera Potrerito S.A.S. en un proceso de responsabilidad civil extracontractual.",
  "palabras_clave": [
    "Corte Constitucional",
    "Sentencia SU-455 de 2020",
    "procedimiento judicial",
    "derecho constitucional"
  ],
  "referencia_legal": "sentencia_su_455_de_2020:00028:4997242600f8"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El problema jurídico abordado en la sentencia SU-455 de 2020 de la Corte Constitucional es la revisión de la decisión de la Sala de Casación Civil de la Corte Suprema de Justicia, que negó el amparo solicitado por la Arrocera Potrerito S.A.S. en un proceso de responsabilidad civil extracontractual. La Corte Constitucional determinó que la sentencia acusada incurrió en un defecto procedimental por exceso ritual manifiesto, un defecto fáctico por indebida valoración probatoria y en violación directa de la Constitución.","palabras_clave":["Corte Constitucional","Sentencia SU-455 de 2020","procedimiento judicial","derecho constitucional"],"referencia_legal":"sentencia_su_455_de_2020:00028:4997242600f8"}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 3 → después 2 · reparación {'suppressed_sentence': 1} · construidas []
**Pasajes declarados por el modelo:** []
**Evidencia:**
1. `sentencia_su_455_de_2020:00042:7edc066fb9bb` — Sentencia SU-455 de 2020 art. None
2. `sentencia_c_55_de_2022:00275:71dec94ba057` — Sentencia C-55 de 2022 art. None
3. `sentencia_c_233_de_2021:00044:2618b7bf6c8e` — Sentencia C-233 de 2021 art. None
4. `sentencia_su_455_de_2020:00014:6e0d8ebf6032` — Sentencia SU-455 de 2020 art. None
5. `sentencia_su_429_de_2024:00114:b5b9b9053928` — Sentencia SU-429 de 2024 art. None
6. `sentencia_su_455_de_2020:00028:4997242600f8` — Sentencia SU-455 de 2020 art. None
7. `sentencia_su_455_de_2020:00013:ac1c4eb073c5` — Sentencia SU-455 de 2020 art. None
8. `sentencia_c_15_de_2018:00011:10a7e8462645` — Sentencia C-15 de 2018 art. None
*Tokens 7288→225 · generación 10033.401399996364 ms · retrieval 18.941299989819527 ms · grafo off*

## 946 · semi_open

**Pregunta:** ¿Cuál es el problema jurídico abordado en la sentencia C-039 de 2025 de la Corte Constitucional? 

**Medición:** cita=cita_ok · legal_basis= Sentencia C-039 de 2025 de la Corte Constitucional

**Respuesta final:**
```json
{
  "respuesta": "El problema jurídico abordado en la sentencia C-039 de 2025 de la Corte Constitucional es la inconstitucionalidad de las normas que reconocen efectos jurídicos a los matrimonios y a las uniones maritales de hecho con o entre personas menores de 18 años.",
  "palabras_clave": [
    "inconstitucionalidad",
    "matrimonios",
    "uniones maritales",
    "menores de 18 años",
    "CEDAW"
  ],
  "referencia_legal": "Sentencia C-39 de 2025; Sentencia C-55 de 2022; Sentencia C-183 de 2025; Sentencia C-15 de 2018; Sentencia C-233 de 2021; Código Civil; Ley 1306 de 2009; Ley 1098 de 2006"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"El problema jurídico abordado en la sentencia C-039 de 2025 de la Corte Constitucional es la inconstitucionalidad de las normas que reconocen efectos jurídicos a los matrimonios y a las uniones maritales de hecho con o entre personas menores de 18 años. La Corte determinó que estas normas desconocían el artículo 16.2 de la Convención sobre la Eliminación de todas las Formas de Discriminación contra la Mujer (CEDAW) y el estándar de mayor protección aplicable a los derechos de los niños y las niñas.","palabras_clave":["inconstitucionalidad","matrimonios","uniones maritales","menores de 18 años","CEDAW"],"referencia_legal":"Sentencia C-39 de 2025","pasajes_usados":["sentencia_c_39_de_2025:00060:cb905c5b4bcf","sentencia_c_39_de_2025:00063:5e8c4e2ffad4"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 3 → después 9 · reparación {'suppressed_sentence': 1} · construidas ['Sentencia C-39 de 2025', 'Sentencia C-55 de 2022', 'Sentencia C-183 de 2025', 'Sentencia C-15 de 2018', 'Sentencia C-233 de 2021', 'Código Civil', 'Ley 1306 de 2009', 'Ley 1098 de 2006']
**Pasajes declarados por el modelo:** ['sentencia_c_39_de_2025:00060:cb905c5b4bcf', 'sentencia_c_39_de_2025:00063:5e8c4e2ffad4']
**Evidencia:**
1. `sentencia_c_39_de_2025:00060:cb905c5b4bcf` — Sentencia C-39 de 2025 art. None
2. `sentencia_c_39_de_2025:00063:5e8c4e2ffad4` — Sentencia C-39 de 2025 art. None
3. `sentencia_c_55_de_2022:00275:71dec94ba057` — Sentencia C-55 de 2022 art. None
4. `sentencia_c_183_de_2025:00011:b145e10d3c7d` — Sentencia C-183 de 2025 art. None
5. `sentencia_c_15_de_2018:00011:10a7e8462645` — Sentencia C-15 de 2018 art. None
6. `sentencia_c_233_de_2021:00044:2618b7bf6c8e` — Sentencia C-233 de 2021 art. None
7. `sentencia_su_277_de_2025:00045:b5fac9c33fa0` — Sentencia SU-277 de 2025 art. None
8. `sentencia_c_80_de_2025:00013:684ca03f17cf` — Sentencia C-80 de 2025 art. None
*Tokens 7378→267 · generación 11791.55080000055 ms · retrieval 26.42139999079518 ms · grafo off*

## 960 · semi_open

**Pregunta:** En el derecho de la protección de la competencia, ¿qué es una "posición dominante"?

**Medición:** cita=cita_ok · legal_basis=Artículo 45 del Decreto 2153 de 1992

**Respuesta final:**
```json
{
  "respuesta": "En el derecho de la protección de la competencia, una \"posición dominante\" se refiere a la capacidad que tiene una empresa o persona de determinar, directa o indirectamente, las condiciones en su respectivo mercado. Esto se establece en el Decreto 780 de 2016, artículo 2.5.6.8. Cuando una empresa ocupa una posición dominante, su comportamiento puede ser regulado para evitar abusos que afecten la libre competencia.",
  "palabras_clave": [
    "posición dominante",
    "derecho de la competencia",
    "Decreto 780 de 2016",
    "abuso de posición dominante"
  ],
  "referencia_legal": "artículo 2.5.6.8 del Decreto 780 de 2016; artículo 2.5.6.9 del Decreto 780 de 2016; artículo 44 del Decreto 2153 de 1992; artículo 66 de la Decisión Andina 486 de 2000; artículo 50 del Decreto 2153 de 1992; Decreto 1663 de 1994; Ley 155 de 1959; Ley 590 de 2000"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "En el derecho de la protección de la competencia, una \"posición dominante\" se refiere a la capacidad que tiene una empresa o persona de determinar, directa o indirectamente, las condiciones en su respectivo mercado. Esto se establece en el Decreto 780 de 2016, artículo 2.5.6.8. Cuando una empresa ocupa una posición dominante, su comportamiento puede ser regulado para evitar abusos que afecten la libre competencia.",
  "palabras_clave": ["posición dominante", "derecho de la competencia", "Decreto 780 de 2016", "abuso de posición dominante"],
  "referencia_legal": "Decreto 780 de 2016, artículo 2.5.6.8",
  "pasajes_usados": [
    "decreto_780_de_2016:01078:099f831ca574",
    "decreto_780_de_2016:01079:ef5746dc55ab"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 16 · reparación {} · construidas ['artículo 2.5.6.8 del Decreto 780 de 2016', 'artículo 2.5.6.9 del Decreto 780 de 2016', 'artículo 44 del Decreto 2153 de 1992', 'artículo 66 de la Decisión Andina 486 de 2000', 'artículo 50 del Decreto 2153 de 1992', 'Decreto 1663 de 1994', 'Ley 155 de 1959', 'Ley 590 de 2000']
**Pasajes declarados por el modelo:** ['decreto_780_de_2016:01078:099f831ca574', 'decreto_780_de_2016:01079:ef5746dc55ab']
**Evidencia:**
1. `decreto_2153_de_1992:00047:66be588e84a7` — Decreto 2153 de 1992 art. 44
2. `decreto_780_de_2016:01079:ef5746dc55ab` — Decreto 780 de 2016 art. 2.5.6.9
3. `decreto_780_de_2016:01078:099f831ca574` — Decreto 780 de 2016 art. 2.5.6.8
4. `decision_andina_486:00065:9e7002ffb5ab` — Decisión Andina 486 de 2000 art. 66
5. `decreto_2153_de_1992:00053:8d78a0ceebf1` — Decreto 2153 de 1992 art. 50
6. `sentencia_c_345_de_2017:00033:8fab44d81ed2` — Sentencia C-345 de 2017 art. None
7. `sentencia_c_345_de_2017:00057:c2f7a8dbad06` — Sentencia C-345 de 2017 art. None
8. `sentencia_sl_648_de_2018:00009:902c784b8318` — Sentencia SL-648 de 2018 art. None
*Tokens 5070→270 · generación 11430.990100008785 ms · retrieval 11.3402999995742 ms · grafo off*

## 991 · semi_open

**Pregunta:** ¿Cuál fue el fundamento jurídico central de la sentencia C-891 del 2012 de la Corte Constitucional? 

**Medición:** cita=cita_ok · legal_basis=Sentencia C-891 del 2012 de la Corte Constitucional

**Respuesta final:**
```json
{
  "respuesta": "El fundamento jurídico central de la sentencia C-891 de 2012 de la Corte Constitucional fue la vulneración del principio de legalidad tributaria. Además, se señaló que esta situación generaba inseguridad jurídica tributaria y afectaba el principio de certeza.",
  "palabras_clave": [
    "principio de legalidad tributaria",
    "autonomía de las entidades territoriales",
    "inseguridad jurídica tributaria"
  ],
  "referencia_legal": "Sentencia C-891 de 2012; Sentencia C-683 de 2015; Sentencia C-164 de 2022; Sentencia C-80 de 2025; Sentencia C-259 de 2015; Constitución Política; Sentencia C-71 de 2015; Sentencia C-931 de 2008"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "El fundamento jurídico central de la sentencia C-891 de 2012 de la Corte Constitucional fue la vulneración del principio de legalidad tributaria. La Corte determinó que la norma demandada violaba la autonomía de las entidades territoriales al permitir que el Ministerio del Interior definiera elementos de los tributos, lo cual contraviene el artículo 287 de la Constitución Política. Además, se señaló que esta situación generaba inseguridad jurídica tributaria y afectaba el principio de certeza.",
  "palabras_clave": ["principio de legalidad tributaria", "autonomía de las entidades territoriales", "artículo 287", "inseguridad jurídica tributaria"],
  "referencia_legal": "Sentencia C-891 de 2012, artículo 287 de la Constitución Política",
  "pasajes_usados": [
    "sentencia_c_891_de_2012:00023:1009f425ace1",
    "sentencia_c_891_de_2012:00000:993ba336d7dc"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 7 → después 9 · reparación {'suppressed_fragment': 3, 'suppressed_sentence': 3} · construidas ['Sentencia C-891 de 2012', 'Sentencia C-683 de 2015', 'Sentencia C-164 de 2022', 'Sentencia C-80 de 2025', 'Sentencia C-259 de 2015', 'Constitución Política', 'Sentencia C-71 de 2015', 'Sentencia C-931 de 2008']
**Pasajes declarados por el modelo:** ['sentencia_c_891_de_2012:00023:1009f425ace1', 'sentencia_c_891_de_2012:00000:993ba336d7dc']
**Evidencia:**
1. `sentencia_c_891_de_2012:00023:1009f425ace1` — Sentencia C-891 de 2012 art. None
2. `sentencia_c_683_de_2015:00164:24bf024c7ba4` — Sentencia C-683 de 2015 art. None
3. `sentencia_c_164_de_2022:00074:dc2ac3b7a018` — Sentencia C-164 de 2022 art. None
4. `sentencia_c_891_de_2012:00000:993ba336d7dc` — Sentencia C-891 de 2012 art. None
5. `sentencia_c_80_de_2025:00060:a7e3ffd20beb` — Sentencia C-80 de 2025 art. None
6. `sentencia_c_259_de_2015:00017:34e9972342a9` — Sentencia C-259 de 2015 art. None
7. `sentencia_su_566_de_2015:00085:6b415202ae46` — Sentencia SU-566 de 2015 art. None
8. `sentencia_c_80_de_2025:00061:ee220a032bb7` — Sentencia C-80 de 2025 art. None
*Tokens 6848→298 · generación 13064.630399996531 ms · retrieval 19.35209998919163 ms · grafo off*

## 1005 · semi_open

**Pregunta:** Con base a la siguiente afirmación, establezca si es falsa o verdadera: 

El Congreso tiene la facultad de efectuar, mediante ley, traslados o adiciones presupuestales, fruto de las cuales se amplíe o cambie la destinación de las apropiaciones de gastos inicialmente autorizados. 

**Medición:** cita=cita_ok · legal_basis=Constitución Política. 

**Respuesta final:**
```json
{
  "respuesta": "La afirmación es verdadera. El Congreso tiene la facultad de efectuar, mediante ley, traslados o adiciones presupuestales, fruto de las cuales se amplíe o cambie la destinación de las apropiaciones de gastos inicialmente autorizados. Esto se establece en el artículo 115 de la Ley 50 de 1990, que faculta al Gobierno para abrir los créditos y efectuar los traslados presupuestales necesarios para el cumplimiento de la ley.",
  "palabras_clave": [
    "Congreso",
    "facultad",
    "traslados presupuestales",
    "ley",
    "apropiaciones"
  ],
  "referencia_legal": "artículo 115 de la Ley 50 de 1990; artículo 57 del Código General Disciplinario; artículo 42 de la Ley 80 de 1993; Sentencia SU-11 de 2020; artículo 347 de la Constitución Política de Colombia de 1991; Ley 1150 de 2007; Sentencia C-772 de 1998; Sentencia C-584 de 2001"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La afirmación es verdadera. El Congreso tiene la facultad de efectuar, mediante ley, traslados o adiciones presupuestales, fruto de las cuales se amplíe o cambie la destinación de las apropiaciones de gastos inicialmente autorizados. Esto se establece en el artículo 115 de la Ley 50 de 1990, que faculta al Gobierno para abrir los créditos y efectuar los traslados presupuestales necesarios para el cumplimiento de la ley.","palabras_clave":["Congreso","facultad","traslados presupuestales","ley","apropiaciones"],"referencia_legal":"Ley 50 de 1990, artículo 115","pasajes_usados":["ley_50_de_1990:00115:a1899933a91d"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 4 → después 14 · reparación {} · construidas ['artículo 115 de la Ley 50 de 1990', 'artículo 57 del Código General Disciplinario', 'artículo 42 de la Ley 80 de 1993', 'Sentencia SU-11 de 2020', 'artículo 347 de la Constitución Política de Colombia de 1991', 'Ley 1150 de 2007', 'Sentencia C-772 de 1998', 'Sentencia C-584 de 2001']
**Pasajes declarados por el modelo:** ['ley_50_de_1990:00115:a1899933a91d']
**Evidencia:**
1. `codigo_disciplinario:00059:190cb268e29a` — Código General Disciplinario (Ley 1952 de 2019) art. 57
2. `ley_50_de_1990:00115:a1899933a91d` — Ley 50 de 1990 art. 115
3. `ley_80_de_1993:00057:15a0c99b9119` — Ley 80 de 1993 art. 42
4. `sentencia_su_11_de_2020:00006:a3d1eabc2812` — Sentencia SU-11 de 2020 art. None
5. `sentencia_su_11_de_2020:00027:67764100bd55` — Sentencia SU-11 de 2020 art. None
6. `sentencia_su_11_de_2020:00004:9b02d13dc549` — Sentencia SU-11 de 2020 art. None
7. `constitucion:00457:fb686f25ce55` — Constitución Política de Colombia de 1991 art. 347
8. `ley_1607_de_2012:00054:9620cf22e7c0` — Ley 1607 de 2012 art. 28
*Tokens 7152→205 · generación 9306.667999990168 ms · retrieval 56.63450001156889 ms · grafo on*

## 1015 · semi_open

**Pregunta:** ¿Qué se requiere para que un aborto sea no punible bajo las causales de la Sentencia C-355 de 2006?

**Medición:** cita=cita_ok · legal_basis=Sentencia C-355 de 2006

**Respuesta final:**
```json
{
  "respuesta": "Para que un aborto sea no punible bajo las causales de la Sentencia C-355 de 2006, se requiere que se cumplan alguna de las tres circunstancias establecidas: (i) que la continuación del embarazo constituya peligro para la vida o la salud de la mujer, certificada por un médico; (ii) que exista grave malformación del feto que haga inviable su vida, certificada por un médico; y, (iii) que el embarazo sea el resultado de una conducta, debidamente denunciada, constitutiva de acceso carnal o acto sexual sin consentimiento, abusivo o de inseminación artificial o transferencia de óvulo fecundado no consentidas, o de incesto. Estas causales se establecen en la Sentencia C-355 de 2006.",
  "palabras_clave": [
    "aborto",
    "causales",
    "Sentencia C-355 de 2006",
    "no punible"
  ],
  "referencia_legal": "Sentencia C-55 de 2022; artículo 9 del Código Penal; Sentencia C-355 de 2006; Constitución Política; Sentencia T-760 de 2008; Sentencia C-313 de 2014"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"Para que un aborto sea no punible bajo las causales de la Sentencia C-355 de 2006, se requiere que se cumplan alguna de las tres circunstancias establecidas: (i) que la continuación del embarazo constituya peligro para la vida o la salud de la mujer, certificada por un médico; (ii) que exista grave malformación del feto que haga inviable su vida, certificada por un médico; y, (iii) que el embarazo sea el resultado de una conducta, debidamente denunciada, constitutiva de acceso carnal o acto sexual sin consentimiento, abusivo o de inseminación artificial o transferencia de óvulo fecundado no consentidas, o de incesto. Estas causales se establecen en la Sentencia C-355 de 2006.","palabras_clave":["aborto","causales","Sentencia C-355 de 2006","no punible"],"referencia_legal":"Sentencia C-55 de 2022","pasajes_usados":["sentencia_c_55_de_2022:00286:b747a94cdda9","sentencia_c_55_de_2022:00265:c06834bfa2de"]}
```
**Parser:** none · correcciones [] · avisos ['semi_open_sentences_2_outside_3_5']
**Citas:** antes 4 → después 10 · reparación {} · construidas ['Sentencia C-55 de 2022', 'artículo 9 del Código Penal', 'Sentencia C-355 de 2006', 'Constitución Política', 'Sentencia T-760 de 2008', 'Sentencia C-313 de 2014']
**Pasajes declarados por el modelo:** ['sentencia_c_55_de_2022:00286:b747a94cdda9', 'sentencia_c_55_de_2022:00265:c06834bfa2de']
**Evidencia:**
1. `sentencia_c_55_de_2022:00312:fb8d22a3b6e4` — Sentencia C-55 de 2022 art. None
2. `codigo_penal:00008:3c39173b1f70` — Código Penal (Ley 599 de 2000) art. 9
3. `sentencia_c_55_de_2022:00025:1b75b530231a` — Sentencia C-55 de 2022 art. None
4. `sentencia_c_355_de_2006:00482:bcee5459959f` — Sentencia C-355 de 2006 art. None
5. `sentencia_c_55_de_2022:00286:b747a94cdda9` — Sentencia C-55 de 2022 art. None
6. `sentencia_c_55_de_2022:00265:c06834bfa2de` — Sentencia C-55 de 2022 art. None
7. `sentencia_c_55_de_2022:00034:eb680fe5efb7` — Sentencia C-55 de 2022 art. None
8. `sentencia_c_55_de_2022:00276:09abf2fa61d8` — Sentencia C-55 de 2022 art. None
*Tokens 7063→318 · generación 13645.585699996445 ms · retrieval 17.874099998152815 ms · grafo off*

## 1065 · semi_open

**Pregunta:** Una ministra a quien le fue aceptada la renuncia continúa celebrando contratos estatales durante dos semanas adicionales. ¿Puede ser sujeto activo de peculado u otros delitos contra la administración pública?

**Medición:** cita=cita_ok · legal_basis=Artículo 20 del Código Penal. 

**Respuesta final:**
```json
{
  "respuesta": "La ministra que renunció y continuó celebrando contratos estatales puede ser sujeto activo de peculado u otros delitos contra la administración pública. Según el artículo 38G del Código Penal, el peculado se refiere a la apropiación de bienes o recursos públicos. Además, el artículo 396C del Código Penal establece que la omisión de información sobre aportes a campañas electorales puede constituir un delito. Sin embargo, la renuncia no impide la responsabilidad penal si se comete un delito durante el periodo de transición.",
  "palabras_clave": [
    "peculado",
    "delitos contra la administración pública",
    "renuncia",
    "Código Penal"
  ],
  "referencia_legal": "artículo 396c del Código Penal; artículo 38g del Código Penal; Sentencia C-15 de 2018; Sentencia C-80 de 2025; artículo 75 del Código de Procedimiento Penal; Ley 1864 de 2017; Ley 1709 de 2014; Ley 1150 de 2007"
}
```
**Salida cruda del modelo:**
```
{"abstencion":false,"respuesta":"La ministra que renunció y continuó celebrando contratos estatales puede ser sujeto activo de peculado u otros delitos contra la administración pública. Según el artículo 38G del Código Penal, el peculado se refiere a la apropiación de bienes o recursos públicos. Además, el artículo 396C del Código Penal establece que la omisión de información sobre aportes a campañas electorales puede constituir un delito. Sin embargo, la renuncia no impide la responsabilidad penal si se comete un delito durante el periodo de transición.","palabras_clave":["peculado","delitos contra la administración pública","renuncia","Código Penal"],"referencia_legal":"Código Penal (Ley 599 de 2000), artículo 38G y 396C","pasajes_usados":["codigo_penal:00511:720189458a3b","codigo_penal:00046:2dd15d07605f"]}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 9 → después 16 · reparación {'suppressed_fragment': 1, 'suppressed_sentence': 1} · construidas ['artículo 396c del Código Penal', 'artículo 38g del Código Penal', 'Sentencia C-15 de 2018', 'Sentencia C-80 de 2025', 'artículo 75 del Código de Procedimiento Penal', 'Ley 1864 de 2017', 'Ley 1709 de 2014', 'Ley 1150 de 2007']
**Pasajes declarados por el modelo:** ['codigo_penal:00511:720189458a3b', 'codigo_penal:00046:2dd15d07605f']
**Evidencia:**
1. `codigo_penal:00511:720189458a3b` — Código Penal (Ley 599 de 2000) art. 396c
2. `sentencia_c_15_de_2018:00038:309304789c09` — Sentencia C-15 de 2018 art. None
3. `codigo_penal:00046:2dd15d07605f` — Código Penal (Ley 599 de 2000) art. 38g
4. `sentencia_c_80_de_2025:00029:f3ba02e0475b` — Sentencia C-80 de 2025 art. None
5. `sentencia_c_15_de_2018:00028:bdd00881d1c7` — Sentencia C-15 de 2018 art. None
6. `sentencia_c_80_de_2025:00034:361ef33ad92d` — Sentencia C-80 de 2025 art. None
7. `codigo_procedimiento_penal:00076:503238c7847a` — Código de Procedimiento Penal (Ley 906 de 2004) art. 75
8. `constitucion:00251:4d6f09faa73a` — Constitución Política de Colombia de 1991 art. 194
*Tokens 6521→248 · generación 10551.871000003302 ms · retrieval 38.014199992176145 ms · grafo on*

## 1073 · semi_open

**Pregunta:** Una empresa contrata a una persona mediante una Cooperativa de Trabajo Asociado para que preste servicios de asesoría jurídica exclusivamente para ella, en horario fijo de lunes a viernes de 8:00 a.m. a 5:00 p.m., bajo instrucciones directas del gerente. ¿Existe una relación laboral?

**Medición:** cita=cita_ok · legal_basis=Artículo 53 de la Constitución Política. 
Artículos 23 y 34 del Código Sustantivo del Trabajo. 

**Respuesta final:**
```json
{
  "respuesta": "La relación laboral se define por la subordinación jurídica, que implica la capacidad del empleador para impartir órdenes y exigir su cumplimiento. En este caso, la persona presta servicios bajo instrucciones directas del gerente, lo que sugiere una relación de subordinación. Además, el horario fijo y la naturaleza exclusiva de los servicios indican una relación de dependencia. Por lo tanto, existe una relación laboral.",
  "palabras_clave": [
    "subordinación",
    "relación laboral",
    "horario fijo",
    "instrucciones directas"
  ],
  "referencia_legal": "Sentencia T-243 de 2018; Sentencia C-201 de 2002; artículo 2 de la Ley 50 de 1990; artículo 2.5.3.10.1.2 del Decreto 780 de 2016; artículo 160 del Código Sustantivo del Trabajo; Sentencia C-934 de 2004; Sentencia T-290 de 1993; Sentencia T-611 de 2001"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "La relación laboral se define por la subordinación jurídica, que implica la capacidad del empleador para impartir órdenes y exigir su cumplimiento. En este caso, la persona presta servicios bajo instrucciones directas del gerente, lo que sugiere una relación de subordinación. Además, el horario fijo y la naturaleza exclusiva de los servicios indican una relación de dependencia. Por lo tanto, existe una relación laboral.",
  "palabras_clave": ["subordinación", "relación laboral", "horario fijo", "instrucciones directas"],
  "referencia_legal": "Sentencia T-243 de 2018, artículo 106, 118 y 119 (parcial) del Código Sustantivo del Trabajo",
  "pasajes_usados": [
    "sentencia_t_243_de_2018:00030:dee4682368d7"
  ]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 5 → después 11 · reparación {'rewritten_to_body': 1} · construidas ['Sentencia T-243 de 2018', 'Sentencia C-201 de 2002', 'artículo 2 de la Ley 50 de 1990', 'artículo 2.5.3.10.1.2 del Decreto 780 de 2016', 'artículo 160 del Código Sustantivo del Trabajo', 'Sentencia C-934 de 2004', 'Sentencia T-290 de 1993', 'Sentencia T-611 de 2001']
**Pasajes declarados por el modelo:** ['sentencia_t_243_de_2018:00030:dee4682368d7']
**Evidencia:**
1. `sentencia_t_243_de_2018:00030:dee4682368d7` — Sentencia T-243 de 2018 art. None
2. `sentencia_c_201_de_2002:00049:95d87ae21c32` — Sentencia C-201 de 2002 art. None
3. `ley_50_de_1990:00001:433e2caf2f79` — Ley 50 de 1990 art. 2
4. `decreto_780_de_2016:00998:fa304fd5e2ae` — Decreto 780 de 2016 art. 2.5.3.10.1.2
5. `codigo_sustantivo_trabajo:00161:3e3de9cca1c2` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 160
6. `codigo_sustantivo_trabajo:00178:a8c88eacee80` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 177
7. `ley_1819_de_2016:00426:0873e973d570` — Ley 1819 de 2016 art. 345
8. `codigo_sustantivo_trabajo:00184:586aca7657aa` — Código Sustantivo del Trabajo (Decreto 2663 de 1950) art. 183
*Tokens 4590→241 · generación 10131.65399999707 ms · retrieval 27.200399999856018 ms · grafo off*

## 1089 · semi_open

**Pregunta:** En el trámite de una apelación ante el Consejo de Estado, el magistrado ponente profiere un auto rechazando la demanda de reconvención. La parte afectada quiere impugnar ese auto. ¿Qué recurso procede, quién lo resuelve y en qué término debe interponerse?

**Medición:** cita=cita_ok · legal_basis=Artículo 246 del CPACA. 

**Respuesta final:**
```json
{
  "respuesta": "El recurso que procede es la súplica, el cual puede interponerse contra el auto que rechaza la demanda de reconvención. Este recurso debe interponerse dentro de los tres (3) días siguientes a la notificación del auto, según el artículo 331 del Código General del Proceso (Ley 1564 de 2012). La súplica será resuelta por los demás integrantes de la sala, sección o subsección de la que haga parte quien profirió el auto recurrido.",
  "palabras_clave": [
    "súplica",
    "recurso",
    "auto",
    "notificación",
    "Consejo de Estado"
  ],
  "referencia_legal": "artículo 331 del Código General del Proceso; artículo 246 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo; artículo 244 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo; artículo 318 del Código General del Proceso; artículo 247 de la Ley 2452 de 2025; Ley 2080 de 2021"
}
```
**Salida cruda del modelo:**
```
{
  "abstencion": false,
  "respuesta": "El recurso que procede es la súplica, el cual puede interponerse contra el auto que rechaza la demanda de reconvención. Este recurso debe interponerse dentro de los tres (3) días siguientes a la notificación del auto, según el artículo 331 del Código General del Proceso (Ley 1564 de 2012). La súplica será resuelta por los demás integrantes de la sala, sección o subsección de la que haga parte quien profirió el auto recurrido.",
  "palabras_clave": ["súplica", "recurso", "auto", "notificación", "Consejo de Estado"],
  "referencia_legal": "Artículo 331 del Código General del Proceso (Ley 1564 de 2012)",
  "pasajes_usados": ["codigo_general_proceso:00339:6f19ebe3ffd7"]
}
```
**Parser:** none · correcciones [] · avisos []
**Citas:** antes 6 → después 14 · reparación {} · construidas ['artículo 331 del Código General del Proceso', 'artículo 246 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'artículo 244 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo', 'artículo 318 del Código General del Proceso', 'artículo 247 de la Ley 2452 de 2025', 'Ley 2080 de 2021']
**Pasajes declarados por el modelo:** ['codigo_general_proceso:00339:6f19ebe3ffd7']
**Evidencia:**
1. `cpaca:00270:f59e2b0321fb` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 246
2. `cpaca:00268:bf7aa1e240d7` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 244
3. `codigo_general_proceso:00339:6f19ebe3ffd7` — Código General del Proceso (Ley 1564 de 2012) art. 331
4. `codigo_general_proceso:00325:c5cdd108a5ab` — Código General del Proceso (Ley 1564 de 2012) art. 318
5. `ley_2452_de_2025:00251:923ae69c11c7` — Ley 2452 de 2025 art. 247
6. `cpaca:00207:2f14d638d576` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 185a
7. `cpaca:00197:67fe2ecd6cba` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 180
8. `cpaca:00310:28d46cec0f2e` — Código de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) art. 282
*Tokens 6061→236 · generación 10256.610600001295 ms · retrieval 20.062800002051517 ms · grafo off*
