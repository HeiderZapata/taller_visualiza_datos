# Estrategia de trabajo y prompts — Taller 2 (Dashboard Analítico)
**Curso:** Visualización de Datos · MCD EAFIT · Equipo: Sara, Yeison, Heider, Kelly + tú
**Enfoque:** riguroso — la estrategia parte de corregir el muestreo antes de construir el mensaje.

---

## 1. Punto de partida (diagnóstico)

El EDA del equipo está bien hecho (pregunta clara, limpieza justificada, feature engineering, 7 hallazgos con implicación de negocio). El problema es la base de datos sobre la que se calculó:

**Confirmado por el código:** la muestra se generó con `USING SAMPLE 500000` = muestreo aleatorio **uniforme por evento**. El archivo oficial `muestra_eventos_def.csv` ES esa muestra. Eso preserva las proporciones globales pero **rompe la estructura de las sesiones y los usuarios**, porque una sesión casi nunca conserva todos sus eventos.

Consecuencia: los hallazgos globales (funnel por categoría, precio, patrón horario — Hallazgos 1 a 4) son confiables, pero los de nivel sesión/usuario (abandono de carrito, recurrencia, velocidad de decisión — Hallazgos 5 a 7) están sesgados. El Hallazgo 5 además tiene cifras contradictorias (código 99%, texto 79% convierte, síntesis 79% abandona).

**Decisión tomada:** no parchamos los hallazgos frágiles ni los descartamos — corregimos la raíz. Generamos una muestra nueva que preserve la estructura y recalculamos todo sobre ella.

---

## 2. Fase 0 — Re-muestreo correcto (paso fundacional)

Este es el primer entregable técnico; todo lo demás depende de él.

**Qué hacer:** volver al CSV crudo `2019-Oct.csv` (~5GB; lo tienen vía el FILE_ID de gdown del notebook) y construir una muestra **por conglomerados a nivel de usuario**: elegir un conjunto aleatorio de `user_id` y traer **todos** sus eventos.

**Por qué por usuario y no por sesión:** un usuario contiene todas sus sesiones, y cada sesión todos sus eventos. Muestrear `user_id` completos preserva a la vez la estructura de sesión (para abandono de carrito y velocidad de decisión) y el historial de compra (para recurrencia one-time vs recurrente). Es la unidad que sostiene los 7 hallazgos.

**Consideraciones:**
- Usar DuckDB (ya lo dominan; maneja los 5GB sin cargar todo en memoria).
- Como solo ~1–3% de usuarios compran, hay que muestrear suficientes usuarios para retener varios miles de eventos `purchase` y que las métricas de sesión/recurrencia sean estables. Apunten a un volumen de eventos comparable al actual (~500k–1M) ajustando el número de usuarios.
- Mantener el muestreo de usuarios **aleatorio simple** (no sobre-muestrear compradores), para no sesgar las tasas del funnel.
- Guardar la nueva muestra en **Parquet** (más rápida y liviana; además alinea con el proyecto integrador). Hacerlo una sola vez y reutilizar.
- Documentar la semilla aleatoria y el número de usuarios para reproducibilidad.

---

## 3. Plan de trabajo (en orden)

0. **Re-muestreo por usuario** desde el crudo y guardar la nueva muestra (Fase 0, arriba).
1. **Re-ejecutar el pipeline de EDA existente** sobre la nueva muestra (reutilizar el código del equipo, solo apuntar al nuevo archivo). No es rehacer el análisis: es recalcular las mismas métricas sobre datos válidos.
2. **Recalcular y comparar los 7 hallazgos:** confirmar que 1–4 se mantienen y obtener por primera vez cifras correctas de 5 (abandono real), 6 (recurrencia real) y 7 (velocidad real). Corregir la redacción contradictoria del Hallazgo 5.
3. **Teoría con lente de rúbrica** (documento de contexto curado): exploratorio vs aclaratorio, Data-to-Ink, atributos preatentivos, storytelling, diseño de dashboard.
4. **Seleccionar UN mensaje central**, ya con todos los hallazgos validados. Candidato fuerte: la tesis del *"usuario persuadible"* — qué categorías tienen intención real pero no cierran, cuándo activar el incentivo por categoría, y (ahora con datos confiables) cuánto tiempo hay para hacerlo dentro de la sesión y a quién vale la pena retener.
5. **Fase II — Aclaratorio:** comparativa exploratoria vs aclaratoria del gráfico central, justificando cada decisión visual.
6. **Fase III — Dashboard (Streamlit):** KPIs arriba, filtros (categoría, hora), narrativa hacia la acción. Prueba de los 30 segundos.
7. **Cierre:** pitch de 3 min, coherencia entre fases, y una nota honesta de que la muestra (aunque ahora bien construida) sigue siendo un subconjunto de octubre — señales sólidas, no verdades definitivas.

---

## 4. Prompts para el proyecto en Claude

### Conocimiento del proyecto (archivos a subir)
- `Contexto_Taller_Visualizacion_curado.md` (marco conceptual).
- El notebook del equipo (`.ipynb`), que tiene el pipeline de EDA reutilizable.
- La descripción del proyecto integrador (e-commerce / propensión / uplift).
- (Después de la Fase 0) la nueva muestra por usuario en Parquet.

### Instrucciones del proyecto (pégalas en "Instrucciones personalizadas")
```
Soy estudiante de la MCD de EAFIT, resolviendo el Taller 2 de Visualización de Datos:
un dashboard analítico sobre clickstream de e-commerce (REES46). Rúbrica: EDA 30%,
Storytelling/Aclaratorio 35%, Dashboard 35%. Criterio de maestría: un gerente decide
una acción en 30 segundos.
Contexto técnico clave: el EDA original usó una muestra POR EVENTO, que rompe las
sesiones. Estamos rehaciendo la base con una muestra POR USUARIO (cluster sampling)
que preserva sesiones e historial de compra, y recalculando los hallazgos sobre ella.
Usa el documento de contexto curado como marco conceptual. Sé crítico con la metodología.
```

### Prompt 1 — Re-muestreo por usuario (Claude Code, sobre el crudo)
```
Tengo el dataset crudo 2019-Oct.csv (~5GB; columnas: event_time, event_type, product_id,
category_id, category_code, brand, price, user_id, user_session). La muestra previa se hizo
POR EVENTO y rompe las sesiones. Con DuckDB, construye una muestra POR USUARIO:
1) obtén los user_id distintos, 2) toma una muestra aleatoria simple de user_id (semilla fija;
ajusta el número para retener ~500k–1M eventos y varios miles de purchase), 3) trae TODOS
los eventos de esos usuarios, 4) guarda el resultado en Parquet (muestra_usuarios.parquet).
Reporta: total de eventos, distribución de event_type, número de usuarios y de sesiones,
y cuántos eventos purchase quedaron. Explica por qué este muestreo preserva la estructura.
```

### Prompt 2 — Re-ejecutar EDA y comparar (Claude Code)
```
Usa muestra_usuarios.parquet y re-ejecuta el pipeline de EDA del notebook del equipo
(limpieza, feature engineering y los 7 hallazgos), apuntando a la nueva muestra. No cambies
la lógica del análisis, solo la fuente de datos. Luego compara los resultados con las cifras
del notebook original y entrégame una tabla: hallazgo, cifra original, cifra nueva, ¿cambió?
Presta especial atención al abandono de carrito (antes 99%/79% contradictorio), al % one-time
(antes 97.1%) y a la velocidad de decisión (antes 5.3 min sobre 489 sesiones). Dime cuáles
hallazgos se sostienen y cuáles cambian con la muestra correcta.
```

### Prompt 3 — Diseño del mensaje (chat del proyecto)
```
Con los 7 hallazgos ya recalculados sobre la muestra por usuario, ayúdame a definir el ÚNICO
mensaje central del dashboard: un argumento que lleve a una decisión de incentivos (a quién,
dónde, cuándo y con qué). Luego diseña la comparativa exploratoria vs aclaratoria del gráfico
principal, justificando cada decisión visual (Data-to-Ink, contraste selectivo, jerarquía,
anotaciones, acto de habla).
```

### Prompt 4 — Construcción del dashboard (Claude Code)
```
Con el mensaje central y los hallazgos validados, construye el dashboard en Streamlit:
KPIs arriba, filtros por categoría y por hora en el sidebar, narrativa que aterriza en la
acción recomendada, estética profesional y coherente. Debe pasar la prueba de los 30 segundos
(la decisión táctica obvia sin manual). Entrégame el app.py estructurado y comentado.
```

---

## 5. Checklist de entrega

- [ ] Fase 0: nueva muestra por usuario generada (Parquet), reproducible, con conteos reportados.
- [ ] EDA re-ejecutado sobre la nueva muestra; tabla comparativa original vs nuevo.
- [ ] Hallazgos 5, 6 y 7 con cifras correctas; contradicción del Hallazgo 5 resuelta.
- [ ] Mensaje central definido sobre hallazgos validados.
- [ ] Fase II: comparativa exploratoria vs aclaratoria justificada.
- [ ] Fase III: dashboard con filtros, KPIs arriba, estética coherente, UX sin sobrecarga.
- [ ] Cada gráfica sigue el patrón Contexto → Hallazgo → Traducción de negocio → Acción.
- [ ] Limitación residual (subconjunto de octubre) comunicada con honestidad.
- [ ] Prueba de los 30 segundos superada.
