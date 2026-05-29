# Contexto curado — Taller de Visualización (Dashboard Analítico)
**Curso:** Visualización de Datos · Maestría en Ciencia de Datos, EAFIT
**Uso:** documento de contexto para el proyecto en Claude. Contiene solo los conceptos del curso relevantes para resolver el taller, organizados por fase de entrega y conectados con el proyecto integrador de e-commerce.

---

## 0. Qué pide el taller y cómo se evalúa

**Misión:** construir un **Dashboard Interactivo** (PowerBI, Looker, Tableau o Python/Streamlit) que responda a un conjunto de **preguntas de negocio estratégicas**. No basta con programar la interfaz: hay que documentar y demostrar la transición desde el **Análisis Exploratorio** (descubrir hallazgos) hasta la **Composición del Mensaje** (Análisis Aclaratorio + Storytelling).

**Criterio de maestría:** la excelencia se alcanza cuando el tomador de decisiones puede responder *"¿qué acción táctica o estratégica debo tomar?"* tras interactuar **30 segundos** con el producto. La navegación debe ser intuitiva e inmediata.

**Tres pilares de evaluación:** Exploración (descubrir hallazgos ocultos) · Mensaje (argumentos visuales aclaratorios orientados a decisión) · Producto (dashboard interactivo funcional).

**Rúbrica:**
- Análisis Exploratorio — **30%**: documentación clara de hallazgos y proceso investigativo.
- Storytelling y Aclaratorio — **35%**: diseño eficiente de la gráfica final, mensaje con jerarquía visual y contraste.
- Desarrollo del Dashboard — **35%**: interactividad, diseño estructurado y usabilidad para el usuario de negocio.

**Datos del taller:** subset `muestra_eventos_def.csv`, derivado del dataset de comportamiento e-commerce (clickstream REES46). El problema integrador es **optimización de la conversión y asignación de incentivos por propensión de compra** (ver §6).

---

## 1. El principio rector: Exploratorio vs. Aclaratorio

Es la distinción central del curso y el eje del taller. Una misma data sirve para dos propósitos opuestos:

| | **Exploratorio** | **Aclaratorio** |
|---|---|---|
| Audiencia | Tú mismo (el analista) | El tomador de decisiones |
| Objetivo | Descubrir patrones sin hipótesis previa | Comunicar un hallazgo específico |
| Gráficas | Rápidas, sucias, muchas, iterativas | Una sola gráfica, un solo mensaje |
| Herramientas Python | Pandas, Seaborn, Matplotlib (una línea) | Plotly `go.Figure`, anotaciones, `update_layout` |
| Función de cada elemento | Reducir el espacio de hipótesis | Cada elemento tiene función retórica |
| Costo del error | Productivo (si no ves nada, aprendiste) | Alto (confundir a la gerencia tiene consecuencias) |

El exploratorio reduce el espacio de posibilidades (de 100 hipótesis descarta 90 y entrega las 10 que merecen rigor). El aclaratorio construye el argumento para que la decisión correcta sea obvia.

**Anatomía de un argumento visual (5 capas).** Es la plantilla mental para pasar de dato a decisión:
1. **Dato** — el hecho crudo ("Abril tuvo 98 ventas").
2. **Contexto** — la referencia comparativa ("la meta era 130"). Sin contexto el dato no significa nada.
3. **Patrón** — la tendencia o anomalía ("único mes bajo la meta en 6 meses").
4. **Significado** — la causa o interpretación ("falló la segmentación del email").
5. **Llamada a la acción** — la consecuencia para el negocio ("corregir y relanzar en mayo"). Sin esto, el análisis es entretenimiento, no herramienta.

**Antes de diseñar cualquier gráfica aclaratoria, responde:** ¿quién es mi audiencia y cuánto sabe de datos? ¿cuál es el único mensaje que quiero que recuerden? ¿qué acción quiero que tomen? ¿cuánto tiempo tienen? ¿qué objeción debo refutar con los datos?

> **El triángulo de la visualización:** el gráfico correcto depende de tres vértices — *qué datos tienes, qué pregunta respondes, quién lo va a leer*.

---

## 2. Fase 1 — Exploración y Hallazgos (30%)

**Objetivo:** identificar el "qué" de los datos. Interrogar el dataset con Pandas/Seaborn/SQL para encontrar señales.
**Entregable:** Jupyter Notebook o reporte Markdown con el EDA y al menos **2 visualizaciones analíticas** + **el hallazgo** explícito (anomalía, tendencia o correlación) que será el centro del dashboard.

### 2.1 Análisis Univariado (una variable)
Responde dónde se concentra, qué tan dispersa está y qué forma tiene.
- **Centralidad:** media (sensible a outliers), mediana (robusta), moda. *Media > mediana → cola a la derecha.*
- **Dispersión:** desviación estándar, rango (sensible), IQR (robusto). *CV = σ/μ > 30% → alta heterogeneidad / posibles subgrupos.*
- **Forma:** skewness (|skew| ≥ 1 → fuertemente asimétrica) y curtosis (leptocúrtica = picos y colas pesadas).
- **Regla de oro:** histograma + boxplot dan el 80% del diagnóstico univariado. Dos picos en el histograma → subgrupos ocultos (bimodalidad).

### 2.2 Análisis Bivariado (dos variables)
- **Numérico vs numérico:** scatter + correlación de Pearson (−1 a 1) + línea de tendencia. *Correlación ≠ causalidad.*
- **Numérico vs categórico:** boxplots agrupados (compara medianas; ordena por mediana para facilitar lectura).
- **Categórico vs categórico:** tabla de contingencia + heatmap (color revela las intersecciones frecuentes; normaliza por fila/columna).

### 2.3 Distribuciones (referencia rápida)
- **Normal:** pilar de inferencia/ML (TLC, residuos OLS, escalado para K-Means/SVM/PCA). Normalidad: Shapiro-Wilk (N<5000), QQ-plot como estándar visual.
- **Poisson:** conteos de eventos en intervalos (demanda, clicks de baja frecuencia, fraude). Si hay muchos ceros → Zero-Inflated Poisson. *Relevante para clickstream: conteo de eventos por sesión.*
- **Uniforme:** máxima incertidumbre en [a, b].

### 2.4 Calidad de Datos (preparación del EDA)
- **Flujo ETL:** Extract (CSV/Parquet/APIs) → Transform (limpieza, imputación, feature engineering; Pandas o PySpark) → Load (Data Warehouse). "Basura entra, basura sale" (GIGO).
- **Tipos de nulos:** MCAR (al azar → borrar o imputar media), MAR (condicionado a otra variable → KNN/media agrupada), MNAR (por el propio valor → imputación predictiva; borrar destruye integridad).
- **Outliers:** Z-Score (|z|>3), IQR (límites Q1−1.5·IQR, Q3+1.5·IQR), Isolation Forest / Mahalanobis (multivariado).
- **Perfilado por columna** (estilo Power Query): % válido / error / vacío, distintos vs únicos.

---

## 3. Fase 2 — Composición del Mensaje (35%)

**Objetivo:** transformar las gráficas exploratorias en **argumentos visuales aclaratorios** diseñados para la gerencia.
**Entregable:** comparativa visual (gráfica exploratoria original **vs.** gráfica aclaratoria final) justificando cada decisión.

### 3.1 Carga cognitiva y Data-to-Ink Ratio
Toda "tinta" que no cuenta una historia es un obstáculo: **menos es más**. Elimina grillas, bordes y ruido. La fórmula del mensaje es **Contexto + Datos + Contraste = Argumento visual**.

> Regla de oro: si el espectador necesita más de 5 segundos para entender el mensaje central, falló el argumento, no el espectador.

### 3.2 Atributos preatentivos (dirigen la mirada en <1s)
- **Color:** se detecta antes de leer → úsalo solo para el elemento MÁS importante.
- **Tamaño:** lo grande se percibe primero → refuerza magnitud.
- **Posición:** arriba-izquierda se lee primero (patrón Z occidental) → pon ahí el insight.
- **Forma:** codifica categorías sin depender del color.

### 3.3 Gestalt (el cerebro agrupa automáticamente)
- **Proximidad:** elementos cercanos se perciben como grupo → usa el espacio en blanco para separar ideas en vez de líneas/cajas.
- **Similitud:** mismo color/forma = misma categoría.
- **Cierre:** el ojo completa figuras incompletas.

### 3.4 Gramática visual
- **Contraste:** tonos neutros (grises) para el contexto, color institucional vibrante **solo** para el dato a resaltar.
- **Jerarquía:** dile a la audiencia dónde mirar 1°, 2°, 3° (títulos grandes/oscuros vs. subtítulos pequeños/grises; treemaps para relación padre-hijo).
- **Recorrido visual:** altera el patrón Z con anotaciones, flechas o líneas de tendencia para forzar el orden de lectura.
- **Balance:** ordena las barras por valor (mayor a menor) salvo orden intrínseco (días, meses). El orden reduce fricción.

### 3.5 Anotaciones y storytelling integrado
Una gráfica sin texto obliga a deducir el mensaje. Las anotaciones lo revelan al instante (ej.: "Caída del servidor AWS — pérdida est. $12k"). Integra el storytelling **dentro** de la gráfica.

**Estructura narrativa (arco dramático):**
1. **Inicio (Contexto)** — escenario base, alinear a la audiencia.
2. **Conflicto (Insight)** — la anomalía/problema descubierto; crea tensión.
3. **Resolución (Acción)** — por qué ocurrió y qué hacer; inspira la decisión.

**Acto de habla** (define el propósito comunicativo):
- **Informar** (declarativo) → describir hechos → "ahora entiendo qué pasó".
- **Convencer** (directivo) → argumentar con razones → "estoy de acuerdo".
- **Motivar** (expresivo) → narrar/storytelling → "¡hagámoslo!".

**De hallazgo a decisión** (patrón obligatorio del taller): Contexto → Hallazgo técnico → **Traducción de negocio** → Acción. Ejemplo: *"La probabilidad de fuga cae 80% tras 3 meses → campaña de descuentos agresiva solo en los primeros 3 meses."*

---

## 4. Fase 3 — Dashboard Interactivo (35%)

**Objetivo:** integrar análisis y gráficas aclaratorias en un producto funcional.
**Requisitos mínimos:** (1) filtros dinámicos (dropdowns/sliders), (2) estética profesional y coherente, (3) responder de forma definitiva a las preguntas de negocio.

### 4.1 Elige el tipo de dashboard según la audiencia
- **Operativo (táctico):** monitoreo en tiempo real, supervisores. Alta granularidad.
- **Analítico (técnico):** científicos/analistas; muchos filtros, drill-down, cruces complejos (ej. cohortes de churn).
- **Estratégico/Ejecutivo (C-level):** decisiones rápidas; minimalista, agregado, centrado en KPIs. Baja granularidad.

*A mayor jerarquía (estratégico), menor granularidad y más síntesis.* Para este taller, orienta el producto al **tomador de decisiones** (estratégico/analítico).

### 4.2 Interactividad
- **Filtros dinámicos:** aíslan porciones (fecha, categoría, segmento); evitan crear 50 gráficas estáticas.
- **Drill-down / roll-up:** cambian la granularidad a voluntad.
- **Tooltips:** esconden el dato crudo hasta que se necesite; mantienen el gráfico limpio.

**Widgets de Streamlit** (si usas Python): `st.selectbox()` / `st.multiselect()` (filtros categóricos), `st.slider()` (rangos numéricos/temporales), `st.button()` / `st.checkbox()` (triggers). Streamlit re-ejecuta el script de arriba a abajo en cada interacción; el valor del widget se asigna a una variable que filtra el DataFrame.

### 4.3 UX — guiar sin sobrecargar
- **Valores por defecto sensatos:** no arranques con un lienzo en blanco (ej. mes por defecto = mes actual).
- **Revelación progresiva:** esconde filtros secundarios en `st.expander()` ("Filtros avanzados"); muestra solo los 2 más importantes.
- **Controles globales en el sidebar:** deja el panel principal para la narrativa visual. Evita el "tablero de control de avión" (20 filtros, 15 gráficas).
- **Layout:** KPIs clave arriba, gráficas de soporte debajo.

---

## 5. Modelo de referencia: dashboard guiado por preguntas de negocio

El curso incluye un caso (seguimiento de proyectos) que es la **plantilla ideal** para estructurar tu dashboard: un panel de filtros globales (multiselect) que alimenta KPIs en tiempo real + una serie de **preguntas de negocio**, cada una resuelta con un tipo de gráfico distinto y una argumentación visual explícita (Contexto + Contraste + Mensaje). Replica este esquema con tus preguntas de e-commerce.

**Mapa pregunta → gráfico (del caso, reutilizable):**

| Pregunta de negocio | Gráfico recomendado | Argumentación visual |
|---|---|---|
| ¿Dónde se concentra/atasca algo por categoría? | Barras apiladas | Color fuerte solo a la categoría crítica; resto en grises |
| ¿Quién/qué es consistente vs. errático? | Box plot por grupo | Caja corta = consistencia; caja larga = variabilidad |
| ¿Dónde está el riesgo (alto X, bajo Y)? | Scatter de cuadrantes | Anota la "zona crítica"; el cuadrante delata atípicos |
| ¿Cómo evoluciona el gasto/volumen en el tiempo? | Áreas apiladas / líneas | El color migra mostrando el "burn rate" |
| ¿Volumen vs. rendimiento? | Combo doble eje (barra + línea) | Barras grises (volumen), línea de color (rendimiento) |
| ¿Cómo fluye el portafolio entre etapas? | Sankey | Ancho de banda = cantidad; trazabilidad extremo a extremo |
| ¿Cómo se distribuye proporcionalmente? | Treemap | Área = magnitud; color = desempeño |
| ¿Relación entre dos numéricas? | Scatter + tendencia | Pearson r; cuidado con causalidad |
| ¿Distribución espacial? | Mapa de burbujas | Tamaño = magnitud, color = desempeño |

**Cheat-sheet univariado:** ¿dónde está el centro? → media/mediana + histograma. ¿Qué tan dispersos? → σ, IQR + boxplot. ¿Forma normal? → skew/curtosis + KDE/QQ-plot. ¿Outliers? → límites IQR + boxplot. ¿Unimodal? → histograma/KDE (dos picos = subgrupos).

---

## 6. Conexión con el proyecto integrador (e-commerce)

**Problema:** la conversión en e-commerce multicategoría es del 1–3%; el ~98% del tráfico no convierte. El reto no es solo vender, sino **asignar incentivos eficientemente** (no descontar a quien ya iba a comprar; no perder al indeciso que un incentivo marginal convertiría). El objetivo es maximizar el GMV incremental y el ROI de marketing vía propensión de compra y **uplift** (efecto causal del incentivo).

**Dataset del taller (`muestra_eventos_def.csv`), variables:** `event_time` (timestamp), `event_type` (view, cart, remove_from_cart, purchase), `product_id`, `category_id`, `category_code`, `brand`, `price`, `user_id`, `user_session`.

**Preguntas de negocio candidatas para el dashboard** (cada una → hallazgo exploratorio → gráfica aclaratoria → acción):
- **Embudo de conversión:** ¿dónde se cae el usuario (view → cart → purchase)? → barras/funnel; acción: dónde intervenir.
- **Propensión por comportamiento:** ¿qué señales (recencia de clics, profundidad de navegación, comparación de marcas) separan a quien compra de quien no? → boxplots agrupados / scatter.
- **Segmentos de incentivo:** ¿qué franja de propensión justifica un cupón (uplift real) y cuál no (cliente leal o causa perdida)? → scatter de cuadrantes (propensión vs. uplift) con "zona de incentivo".
- **GMV y categorías/marcas:** ¿dónde se concentra el valor y dónde hay fuga? → treemap / barras ordenadas.
- **Comportamiento temporal:** ¿cómo varían eventos y conversión por hora/día? → líneas/áreas; acción: cuándo lanzar el nudge.

**El mensaje final del dashboard** debe permitir que un gerente responda en 30 segundos: *"¿a qué segmento lanzo incentivos y a cuál no, para maximizar el GMV sin erosionar margen?"*

---

## 7. Checklist de entrega

- [ ] **Pregunta de negocio** definida con claridad (qué problema resuelve el dashboard).
- [ ] **Fase 1:** ≥2 visualizaciones exploratorias + hallazgo explícito documentado (notebook/Markdown).
- [ ] **Fase 2:** comparativa exploratoria vs. aclaratoria con justificación (Data-to-Ink, contraste, jerarquía, anotaciones).
- [ ] **Fase 3:** dashboard con filtros dinámicos, KPIs arriba, estética coherente, UX sin sobrecarga.
- [ ] Cada gráfica del dashboard sigue el patrón **Contexto → Hallazgo → Traducción de negocio → Acción**.
- [ ] Prueba de los 30 segundos: la acción recomendada es evidente sin manual.
