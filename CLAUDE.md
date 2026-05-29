# CLAUDE.md — Contexto operativo para Claude Code

> Este archivo lo lee Claude Code automáticamente al iniciar. Son **instrucciones de trabajo** para el agente.
> La bitácora y el estado del proyecto viven en `docs/ESTADO_PROYECTO.md` (léelo al empezar cualquier tarea).

## Qué es este proyecto
Taller 2 de Visualización de Datos (MCD EAFIT). Construimos un **dashboard analítico en Streamlit** sobre clickstream de e-commerce (REES46, oct 2019) que lleve a un gerente a una decisión de incentivos en 30 segundos: a quién, dónde, cuándo y con qué incentivar para subir la conversión.

## Reglas críticas de datos (no romper)
- **`data/raw/2019-Oct.csv` pesa ~5 GB. NUNCA lo cargues completo en memoria ni con `pandas.read_csv` sobre el archivo entero.** Procésalo siempre con **DuckDB** (streaming, sin cargar todo en RAM).
- Datos crudos en `data/raw/` son **inmutables**: no se editan ni se sobreescriben.
- Todo lo derivado va a `data/processed/`. Los datos (`*.csv`, `*.parquet`) **no se versionan en git** (ya están en `.gitignore`); son reproducibles desde la semilla.

## Decisión metodológica central (por qué rehacemos la base)
La muestra original (`muestra_eventos_def.csv`) se generó con `USING SAMPLE 500000` = **muestreo uniforme por evento**, que **rompe sesiones y usuarios**. Por eso los hallazgos de nivel sesión/usuario quedaron sesgados.
- **Re-muestreamos POR USUARIO** (cluster sampling): se eligen `user_id` al azar y se traen **todos** sus eventos. Esto preserva sesiones (abandono, velocidad) e historial de compra (recurrencia).
- **Muestreo aleatorio simple de usuarios** (NO sobre-muestrear compradores; eso sesgaría las tasas del funnel).
- **Semilla fija** y **número de usuarios** documentados para reproducibilidad. Parámetros en `config.py`.

## Parámetros del proyecto (fuente única: `config.py`)
- `SEED = 42`
- `TARGET_EVENTS ≈ 1_000_000` (≈15k purchases esperadas; el `n_users` se calibra tras contar usuarios/eventos del crudo).
- Antes de fijar `n_users`, correr una pasada de conteo en DuckDB:
  `SELECT count(*) AS eventos, count(DISTINCT user_id) AS usuarios, count(*)*1.0/count(DISTINCT user_id) AS ev_x_usuario FROM read_csv_auto('data/raw/2019-Oct.csv');`
  y resolver `n_users = round(TARGET_EVENTS / ev_x_usuario)`.

## Fix metodológico del funnel (A1) — obligatorio al re-ejecutar el EDA
El funnel original (sección 4.1 del notebook) calcula cocientes de **conteos de eventos** (`purchase_events / view_events`), con `cart_rate` y `conv_rate` colgando ambas de `views`. **No es un funnel de unidades.**
- Reescribir como **funnel por unidad**: a nivel **sesión** (de las sesiones con view, cuántas con cart; de esas, cuántas con purchase) o, ideal, **producto dentro de la sesión** (view P → cart P → purchase P).
- Clasificar cada unidad por su **etapa más profunda** y **encadenar** cart→purchase.
- Afecta Hallazgo 1 y la `conv_rate` que usa el Hallazgo 2.

## Validez de los 7 hallazgos
- **Robustos (solo re-ejecutar):** 3 y 4 (patrón horario, global y por categoría).
- **Robusto pero recalcular tras el fix A1:** 2 (precio no es el freno). Además, filtrar categorías con <500 vistas en el scatter precio vs conversión.
- **Recalcular (dependen de sesión/usuario):** 5 (abandono — resolver la triple contradicción 99% / 79% / 79%), 6 (recurrencia, hoy 97.1% one-time), 7 (velocidad, hoy 5.3 min sobre 489 sesiones contaminadas).

## Estructura del repositorio
```
.
├── CLAUDE.md                 # este archivo
├── README.md
├── config.py                 # SEED, TARGET_EVENTS, rutas (fuente única)
├── requirements.txt
├── data/
│   ├── raw/                  # 2019-Oct.csv (~5GB) — NO a git, NO cargar completo
│   └── processed/            # muestra_usuarios.parquet — NO a git
├── docs/                     # ESTADO_PROYECTO.md (punto de entrada), Estrategia, Contexto
├── notebooks/
│   └── taller_2.ipynb        # EDA del equipo: AQUÍ se ajusta (Fase 1). Importa funnel.py
├── src/
│   ├── sampling.py           # Fase 0: re-muestreo por usuario (DuckDB), corre una sola vez
│   └── funnel.py             # A1: función de funnel por unidad. La usan el notebook Y el dashboard
├── outputs/figures/          # gráficas exploratorias y aclaratorias
└── app/app.py                # Fase 3: dashboard Streamlit
```

## Orden de ejecución (no adelantar fases sin que el usuario lo pida)
0. **Fase 0** — `src/sampling.py`: contar usuarios/eventos → calibrar `n_users` → muestrear por usuario con semilla → guardar `data/processed/muestra_usuarios.parquet`. Reportar: total eventos, distribución de `event_type`, nº usuarios, nº sesiones, nº `purchase`.
1. **Fase 1** — en `notebooks/taller_2.ipynb`: re-ejecutar el pipeline del notebook sobre la nueva muestra (misma lógica, nueva fuente) e **implementar A1** importando la función de `src/funnel.py`. El EDA vive en el notebook; los `.py` son soporte.
2. Tabla comparativa de los 7 hallazgos (original vs nuevo); resolver contradicción del Hallazgo 5.
3. Definir mensaje central (candidato: "usuario persuadible").
4. Fase II — comparativa exploratorio vs aclaratorio del gráfico principal.
5. Fase III — `app/app.py`: dashboard (KPIs arriba, filtros en sidebar, prueba de 30 s).

## Convenciones para el agente
- **Entorno:** el proyecto usa un venv propio en `.venv/` (no un Python global como `learning`). Antes de instalar paquetes o ejecutar scripts, verifica que esté activado (debe verse `(.venv)` en el prompt y `python -c "import sys; print(sys.executable)"` debe apuntar al `.venv` del repo). Si la activación no persiste entre comandos, invoca el intérprete del venv directamente: `.venv/Scripts/python.exe`.
- Lee `docs/ESTADO_PROYECTO.md` al iniciar cada tarea; actualízalo (tablero + bitácora con fecha) al cerrar una fase.
- No inventes cifras: si un número no está validado sobre la nueva muestra, dilo. Marca supuestos.
- Aplica los principios del curso (`docs/Contexto_Taller_Visualizacion_curado.md`) al diseñar gráficas: Data-to-Ink, atributos preatentivos, jerarquía, Gestalt, acto de habla, patrón Contexto→Hallazgo→Traducción de negocio→Acción.
- Trabaja sobre la rama de la persona (no `main`). Sugiere commits pequeños y descriptivos.
- **Notebooks en git:** limpiar las salidas (outputs) antes de cada commit para evitar diffs ruidosos y conflictos de merge entre ramas (`nbstripout` o "Clear All Outputs").
- Pide permiso antes de instalar paquetes o correr comandos pesados.
