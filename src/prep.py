"""
src/prep.py — FASE III: carga + limpieza + feature engineering de la muestra.

Porta el pipeline del notebook (Fase I: carga, limpieza y feature engineering) a una
función reutilizable, para que el dashboard reporte EXACTAMENTE las mismas cifras que el
EDA. NO importa streamlit (el caché se aplica en app/app.py). La raíz del repo se inserta
en sys.path igual que en src/sampling.py.

Fórmulas idénticas a las celdas del notebook:
  - carga + event_time tz-naive
  - drop_duplicates() + filtro price > 0
  - hour / day_of_week / date / category_main
"""
import sys
from pathlib import Path

import pandas as pd

# Permite importar config.py desde la raíz del repo
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402


def load_sample(path=config.SAMPLE_PARQUET):
    """Carga la muestra por usuario, la limpia y agrega features; devuelve un DataFrame.

    Replica el pipeline del notebook:
      1. lee el parquet (Fase 0),
      2. event_time -> datetime UTC -> tz-naive (todo el dataset es UTC),
      3. elimina duplicados exactos,
      4. filtra precios en cero (price > 0),
      5. agrega hour, day_of_week, date y category_main (1er nivel de category_code).

    El parquet (~28 MB / ~982k filas) cabe en memoria; la regla de los 5 GB es solo para
    el CSV crudo.
    """
    df = pd.read_parquet(path)

    # event_time a datetime tz-naive (habilita hour/day_of_week y los deltas de tiempo)
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True).dt.tz_localize(None)

    # Limpieza
    df = df.drop_duplicates()
    df = df[df["price"] > 0]

    # Feature engineering
    df["hour"] = df["event_time"].dt.hour
    df["day_of_week"] = df["event_time"].dt.day_name()
    df["date"] = df["event_time"].dt.date
    df["category_main"] = df["category_code"].str.split(".").str[0]

    return df.reset_index(drop=True)
