"""
config.py — Fuente única de parámetros y rutas del proyecto.
Todo script (sampling, eda, dashboard) debe leer de aquí; no repetir números mágicos.
"""
from pathlib import Path

# ── Reproducibilidad ──────────────────────────────────────────────────────────
SEED = 42  # semilla fija para el muestreo por usuario (documentada para reproducir)

# ── Objetivo de tamaño de la muestra ─────────────────────────────────────────
# Apuntamos a ~1M de eventos (≈15k purchases esperadas). El NÚMERO DE USUARIOS no
# se fija a mano: se calibra en runtime = round(TARGET_EVENTS / eventos_por_usuario),
# tras contar usuarios y eventos del crudo. Ver src/sampling.py.
TARGET_EVENTS = 1_000_000

# ── Rutas (relativas a la raíz del repo) ─────────────────────────────────────
ROOT = Path(__file__).resolve().parent

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "outputs" / "figures"

RAW_CSV = DATA_RAW / "2019-Oct.csv"            # crudo ~5GB (inmutable, no versionado)
SAMPLE_PARQUET = DATA_PROCESSED / "muestra_usuarios.parquet"  # salida de la Fase 0
