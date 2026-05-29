# Taller 2 — Dashboard Analítico de Conversión (e-commerce REES46)

Maestría en Ciencia de Datos · EAFIT · Visualización de Datos
Equipo: Sara Rendón, Yeison Londoño, Heider Zapata, Kelly Enríquez

## Qué es
Dashboard interactivo (Streamlit) sobre clickstream de e-commerce (REES46, octubre 2019) que responde preguntas de negocio sobre **dónde, cuándo y a quién incentivar** para aumentar la conversión. Documenta la transición de Análisis Exploratorio → Composición del Mensaje (Aclaratorio + Storytelling).

**Criterio de calidad:** un gerente debe poder decidir una acción táctica en 30 segundos interactuando con el dashboard.

## Contexto metodológico importante
La muestra original se generó **por evento** (`USING SAMPLE 500000`), lo que rompe sesiones y usuarios. Este proyecto **re-muestrea por usuario** (cluster sampling) desde el crudo `2019-Oct.csv`, preservando sesiones e historial de compra, y recalcula los hallazgos sobre esa base. Ver `docs/ESTADO_PROYECTO.md`.

## Estructura
```
config.py            Parámetros (semilla, target de eventos, rutas)
data/raw/            2019-Oct.csv (~5GB) — no versionado
data/processed/      muestra_usuarios.parquet — no versionado, reproducible
docs/                Estado, estrategia y marco conceptual del proyecto
notebooks/           Notebook del EDA (taller_2.ipynb)
src/                 Scripts de soporte (sampling, funnel)
outputs/figures/     Gráficas exploratorias y aclaratorias
app/                 Dashboard Streamlit
```

## Requisitos
- Python 3.10+.
- **Entorno virtual propio del proyecto** (no usar uno global, para reproducibilidad):
  ```bash
  python -m venv .venv
  source .venv/Scripts/activate     # Git Bash en Windows · (Linux/Mac: source .venv/bin/activate)
  pip install -r requirements.txt
  ```
  En VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → elige el `.venv` del proyecto
  (así la terminal integrada y el notebook lo activan solos).
- El crudo `2019-Oct.csv` en `data/raw/` (se descarga una sola vez con `gdown`; no se versiona).

## Cómo correr (en orden)
```bash
# 0. Re-muestreo por usuario → data/processed/muestra_usuarios.parquet (corre una vez)
python src/sampling.py

# 2. Dashboard
streamlit run app/app.py
```
**Fase 1 (EDA):** se hace en el notebook `notebooks/taller_2.ipynb`, re-ejecutándolo sobre la nueva muestra e importando el funnel por unidad desde `src/funnel.py`. El EDA es el entregable narrativo; los scripts `.py` son soporte (muestreo y función de funnel compartida con el dashboard).

> Nota para el equipo: limpiar las salidas del notebook antes de cada commit (`nbstripout` o "Clear All Outputs") para evitar conflictos de merge entre ramas.

## Datos y reproducibilidad
Los datos pesados **no se versionan** (ver `.gitignore`); son reproducibles desde la semilla fija definida en `config.py`. Lo que se versiona es el código + la semilla. La muestra abarca solo octubre: las señales son sólidas pero no definitivas.

## Documentación del proyecto
- `docs/ESTADO_PROYECTO.md` — punto de entrada: estado, decisiones, validez de hallazgos, próxima acción.
- `docs/Estrategia_y_prompts_Taller2.md` — plan por fases y prompts.
- `docs/Contexto_Taller_Visualizacion_curado.md` — marco conceptual del curso.
