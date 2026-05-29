# Estado del proyecto — Taller 2: Dashboard Analítico
**Última actualización:** 2026-05-29 · **Actualizado por:** Claude Code (Fase 1: 4.1 funnel A1)
**Documentos hermanos:** `Contexto_Taller_Visualizacion_curado.md` (marco conceptual) · `Estrategia_y_prompts_Taller2.md` (plan y prompts)

---

## Cómo usar y mantener este documento
- **Al iniciar CUALQUIER chat del proyecto:** lee COMPLETO este documento **y todos los insumos listados abajo** antes de actuar. No basta con las secciones 1–6: el notebook del EDA es la fuente de las cifras y de los problemas metodológicos que estamos corrigiendo.
- **Al cerrar un chat o terminar una fase:** actualiza el tablero (sección 4), marca tareas (sección 6) y añade una entrada en la bitácora (sección 7) con fecha. Cambia el encabezado "Última actualización".
- Mantenlo corto y veraz: refleja lo que REALMENTE está hecho, no lo planeado.

### Insumos del proyecto (leer TODOS al iniciar)
- **`ESTADO_PROYECTO.md`** (este) — punto de entrada: contexto, decisiones, validez de hallazgos, tablero, próxima acción.
- **`Contexto_Taller_Visualizacion_curado.md`** — marco conceptual del curso (exploratorio vs aclaratorio, Data-to-Ink, preatentivos, Gestalt, jerarquía, acto de habla, diseño de dashboard).
- **`Estrategia_y_prompts_Taller2.md`** — plan por fases y prompts. Se sigue ese orden; no se adelantan fases sin que el usuario lo pida.
- **`taller_2.pdf`** — export del notebook del EDA del equipo (formato real: `.zip` con HTML/imágenes, 28 páginas). Contiene el pipeline reutilizable (limpieza, feature engineering) y los 7 hallazgos originales con su código. **Es la fuente de verdad de lo que hay HOY que estamos corrigiendo.**
- **`02_Contendio_curso_sum.md`** — ⚠️ **DUPLICADO exacto** de `Contexto_Taller_Visualizacion_curado.md`. Redundante; no tratar como fuente distinta.
- **(Tras Fase 0)** `muestra_usuarios.parquet` — nueva muestra por usuario.

---

## 1. Contexto (resumen)
- **Entregable:** dashboard interactivo (Streamlit) que responda preguntas de negocio estratégicas, documentando la transición de Análisis Exploratorio → Composición del Mensaje (Aclaratorio + Storytelling).
- **Rúbrica:** EDA 30% · Storytelling/Aclaratorio 35% · Dashboard 35%. **Criterio de maestría:** el gerente decide una acción en 30 segundos.
- **Problema:** e-commerce multicategoría; conversión 1–3%; objetivo = identificar a quién/cuándo/cómo incentivar (propensión + uplift). Conecta con el proyecto integrador.
- **Datos:** clickstream REES46 (oct 2019). El subset original `muestra_eventos_def.csv` quedó descartado como base (ver decisión D1). El crudo `2019-Oct.csv` (~5GB) está en Google Drive con `FILE_ID = 1kDasOXgXimvPn2Shu3wgZymbqj4_8pDc` (gdown). Volumen de referencia de la muestra actual (para dimensionar la nueva): ~499.212 eventos tras limpieza, 8.607 `purchase`, 10.851 `cart`, 8.340 usuarios compradores.
- **Equipo:** Sara, Yeison, Heider, Kelly + tú.

---

## 2. Decisiones tomadas
- **D1 — Muestreo:** se re-muestrea **por usuario** (cluster sampling) desde el crudo `2019-Oct.csv`, conservando todos los eventos de cada usuario. Motivo: la muestra original era aleatoria por evento y rompía sesiones/usuarios. Preservar usuarios completos sostiene los 7 hallazgos.
- **D2 — Mensaje:** se ancla en hallazgos validados; candidato central = tesis del "usuario persuadible" (qué categorías tienen intención real y no cierran; cuándo y cómo incentivar).
- **D3 — Herramienta del dashboard:** Streamlit/Python.

---

## 3. Hallazgos y su validez
| # | Hallazgo | Tipo | Estado |
|---|----------|------|--------|
| 1 | Funnel y conversión por categoría | Global, pero mal definido (ver A1) | ✅ Recalculado con funnel por unidad (4.1). Mensaje corregido: persuadible = electronics/computers, NO construction. Ver §7 |
| 2 | El precio no es el freno | Global | Robusto; recalcular conv_rate tras A1 |
| 3 | Ventana horaria global (pico 7–11h) | Marginal | Robusto; solo re-ejecutar |
| 4 | Ventana horaria por categoría | Marginal | Robusto; solo re-ejecutar |
| 5 | Abandono de carrito | Sesión | Recalcular con muestra nueva; resolver triple contradicción (código 99.0% abandono vs texto H5 "79% convierte/21% abandona" vs síntesis "79% abandona"). El 99% está inflado por el muestreo por evento |
| 6 | One-time vs recurrentes (97.1%) | Usuario | Recalcular con muestra nueva |
| 7 | Velocidad de decisión (5.3 min) | Sesión | Recalcular con muestra nueva |

---

## 4. Tablero de fases
| Fase | Descripción | Estado | Notas |
|------|-------------|--------|-------|
| 0 | Re-muestreo por usuario (Parquet) | ✅ Hecho | n_users=71.199 (semilla 42); 982.106 eventos, 16.925 purchase. Ver §7 |
| 1 | Re-ejecutar EDA sobre nueva muestra | 🟡 En progreso | Hechas: carga (parquet), calidad+limpieza (1–3), 4.1 funnel. Siguiente: 4.2 |
| 1b | Reescribir funnel 4.1 (ver A1) | ✅ Hecho | Funnel por unidad (producto-en-sesión) en `src/funnel.py`; usado en 4.1. Ver §7 |
| 2 | Validar/comparar los 7 hallazgos | ⬜ Pendiente | Tabla original vs nuevo |
| 3 | Seleccionar mensaje central | ⬜ Pendiente | Tras validar |
| 4 | Fase II — Aclaratorio (comparativa) | ⬜ Pendiente | |
| 5 | Fase III — Dashboard Streamlit | ⬜ Pendiente | KPIs, filtros, 30 seg |
| 6 | Pitch 3 min + coherencia | ⬜ Pendiente | |

Leyenda: ⬜ pendiente · 🟡 en progreso · ✅ hecho

---

## 5. Ajustes de código del EDA (además del re-muestreo)

(Ver PDF Taller 2 -> es el Notebook ipynb que contiene el EDA)

**A1 — Funnel y conversión por categoría (4.1): REESCRIBIR.**
Hoy calcula cocientes de conteos de eventos (`purchase_events / view_events`), no un funnel de unidades. No clasifica a cada usuario/sesión por su etapa más profunda, así que el denominador (views) está inflado por multi-vistas y no se lee como "% de visitantes que compran". Además `cart_rate` y `conv_rate` cuelgan ambas de views en vez de encadenar (cart→purchase sobre los que llegaron a cart).
- **Confirmado en el código (pág. 11 del notebook):** `conv_df['conv_rate'] = purchases/views` y `conv_df['cart_rate'] = carts/views`; el funnel global izquierdo usa `value_counts()` de `event_type` y `pct = val/views`. Son conteos de eventos, sin encadenar.
- Fix: calcular el funnel a nivel **sesión** (de las sesiones con view, cuántas con cart, y de esas cuántas con purchase) o, ideal, **producto dentro de la sesión** (view P → cart P → purchase P).
- Impacto: afecta Hallazgo 1 y la `conv_rate` que usa el Hallazgo 2.

**A1-bis — Muestreo comentado ≠ ejecutado (dejar claro en el notebook nuevo).**
El notebook tiene un comentario que describía un muestreo estratificado ("100% de purchase/cart + 2% de view"), pero el código realmente ejecutado fue `USING SAMPLE 500000` = **uniforme por evento**. No afirmar que la muestra es estratificada; lo es uniforme por evento (de ahí D1).

**A2 — Lógica correcta, solo requiere la muestra nueva (+ refinamiento opcional):**
- 4.5 Abandono de carrito: la resta de conjuntos de sesiones es correcta; dará cifra real con datos intactos. **Confirmado el daño del muestreo:** el código imprime 99.0% de abandono porque, al caer eventos sueltos, muchas sesiones conservan solo el `cart` y pierden su `purchase`. Opcional: nivel producto. Resolver la triple contradicción de redacción (ver tabla §3).
- 4.6 Recurrencia: `groupby('user_id')` correcto; válido con muestra por usuario. Hoy da 97.1% one-time (8.102 vs 238), inflado por el muestreo + ventana solo-octubre.
- 4.7 Velocidad de decisión: válido con sesiones intactas. **Evidencia directa del daño:** el propio notebook descarta 185 de 674 sesiones (27%) por tiempos negativos, que llama "artefactos de la muestra aleatoria"; la mediana de 5.3 min vive sobre 489 sesiones contaminadas. Opcional: medir por producto (first view de P → purchase de P) en vez de first view de la sesión.
- 4.2 Precio vs conversión (Hallazgo 2): el scatter incluye categorías con muy pocas vistas (stationery 72, country_yard 174, medicine 184) porque el `join` usó la tabla sin filtrar; el funnel sí exigía ≥500 vistas. Aplicar el mismo umbral ≥500 para un read limpio. La conclusión cualitativa ("el precio no es el freno") probablemente aguanta, pero las cifras dependen del fix A1.

**A3 — Sin cambios, solo re-ejecutar:**
- 4.3 y 4.4 Patrones temporales: distribuciones marginales de eventos `purchase`; correctas.
- Limpieza (duplicados, precio=0) y feature engineering (hour, day_of_week, date, category_main): re-aplicar sobre la nueva muestra.

**A4 — Caveats transversales a dejar escritos en el notebook:**
- Ventana = solo octubre (un "one-time" podría comprar en noviembre).
- "first view → first purchase" puede cruzar productos distintos en la misma sesión.
- 31.8% de eventos sin `category_main` se excluyen del análisis por categoría.

**A5 — Cosmético:**
- Subtítulos mal numerados: los `suptitle` dicen "5.3 Patron Temporal" y "5.4 Patron de Compras por Hora" en secciones que son 4.3 y 4.4 (confirmado).

---

## 6. Próxima acción (tareas abiertas)
- [x] Revisar todos los insumos del proyecto, incluido el notebook del EDA (hecho 2026-05-28).
- [x] Definir número de usuarios a muestrear: contados 3.022.290 usuarios / 42.448.764 eventos en el crudo (14.05 ev/usuario) → n_users=71.199 calibrado para ~1M eventos (hecho 2026-05-28).
- [x] Ejecutar Fase 0 (re-muestreo) y guardar `muestra_usuarios.parquet` (semilla fija documentada) (hecho 2026-05-28).
- [x] Implementar A1 (funnel por unidad) al re-ejecutar el EDA (hecho 2026-05-29, `src/funnel.py` + 4.1).
- [ ] Adaptar 4.2 (precio vs conversión) a `cat_funnel`, aplicar umbral ≥500 unidades, recalcular Hallazgo 2.
- [ ] Recalcular hallazgos de sesión/usuario: 4.5 abandono, 4.6 recurrencia, 4.7 velocidad.
- [ ] Reescribir 4.8 síntesis y revisar mensaje central (D2) con el giro del Hallazgo 1.
- [ ] Producir tabla comparativa de los 7 hallazgos (original vs nuevo).

---

## 7. Bitácora de avance
- **2026-05-28** — Planeación. Confirmado que la muestra original es por evento y rompe sesiones; decidido re-muestrear por usuario (D1). Revisado el código del EDA: identificado que el funnel (4.1) requiere reescritura metodológica además del re-muestreo (A1). Creados los 3 documentos del proyecto. Pendiente: ejecutar Fase 0.
- **2026-05-28** — **Fase 0 ejecutada** (`src/sampling.py`, DuckDB streaming, semilla 42). Conteo del crudo: 42.448.764 eventos / 3.022.290 usuarios (14.05 ev/usuario) → n_users calibrado=71.199 para target ≈1M eventos. Muestra por usuario resultante: **982.106 eventos**, **71.199 usuarios**, **214.759 sesiones**; distribución event_type: view 943.903 (96.11%), cart 21.278 (2.17%), purchase 16.925 (1.72%). Guardada en `data/processed/muestra_usuarios.parquet` (28.1 MB, no versionada). Nota operativa: el script imprime emojis y falló al inicio por la consola Windows (cp1252); se re-ejecutó con `PYTHONUTF8=1`. Próximo: Fase 1 (re-ejecutar EDA sobre esta muestra + implementar A1). Entorno en venv propio `.venv/` (Python 3.14.5).
- **2026-05-28** — Revisión completa de insumos (incl. notebook `taller_2.pdf`, export HTML de 28 págs). Confirmados todos los diagnósticos previos y añadido detalle: (a) el muestreo ejecutado fue `USING SAMPLE 500000` uniforme por evento, distinto del estratificado que sugería un comentario (A1-bis); (b) A1 verificado en el código (cart_rate y conv_rate cuelgan de views, sin encadenar); (c) Hallazgo 5 tiene triple contradicción real (99.0% / 79% / 79%) y el 99% está inflado por el muestreo; (d) Hallazgo 7 — el equipo ya descartó 27% de sesiones por tiempos negativos ("artefactos de la muestra"), evidencia directa del daño; (e) Hallazgo 2 — el scatter incluye categorías con <500 vistas que deben filtrarse; (f) `02_Contendio_curso_sum.md` es duplicado exacto de `Contexto_curado`; (g) guardado el FILE_ID del crudo y el volumen de referencia de la muestra actual. Actualizado este documento para que al iniciar cada chat se lean TODOS los insumos. Próximo paso sin cambios: Fase 0.
- **2026-05-29** — **Fase 1 en progreso sobre la muestra por usuario.** Hechas y corregidas las secciones del notebook: (a) **narrativa de muestreo** (celdas 3–11) documentando el cambio por-evento→por-usuario; (b) **carga** (celda 12) lee el parquet vía `config.py`, normaliza `event_time` a datetime; (c) **calidad+limpieza** (1–3): hardcoded reemplazados por cálculo dinámico — nulos `category_code` 31.98%, `brand` 14.38%, duplicados 564 (0.06%); gráficas de calidad re-etiquetadas a "nivel evento" y precio cambiado a **por producto único** (decisión metodológica: ver memoria del proyecto). (d) **A1 implementado**: `src/funnel.py` (`global_funnel`, `category_funnel`) con unidad = **producto dentro de sesión**, clasificación por etapa más profunda y tasas encadenadas; usado en 4.1. **Resultados del funnel por unidad:** 642.169 unidades; cart_rate 3.61%, conv_rate 2.44%, cart→purchase 67.6%; partición 96.39% solo-vista / 1.17% carrito-sin-compra / 2.44% compra. Por categoría (conv_rate): electronics 3.92% (cart 6.12, cierre 64%), appliances 2.38%, computers 1.53% (peor cierre 61.3%), apparel 0.52% (cierre 100% → freno upstream/vitrina). **Giro de mensaje:** el "persuadible" (carrito abandonado) se concentra en electronics (~5.048 unid, ~67% del total) y appliances, NO en construction (~70). El slopegraph (celda 28) pasó a dinámico desde `cat_funnel`, protagonista=electronics **provisional** (variable `HIGHLIGHT`). Pendiente al retomar: **4.2** (adaptar a `cat_funnel`, umbral ≥500, Hallazgo 2). Nota operativa de flujo: como el notebook con outputs supera el límite de lectura, antes de cada tanda de ediciones se corre `nbstripout` y el usuario re-ejecuta.
