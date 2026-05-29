"""
src/sampling.py — FASE 0: re-muestreo POR USUARIO (cluster sampling).

Por qué: la muestra original se hizo por evento (USING SAMPLE 500000), lo que rompe
sesiones y usuarios. Aquí elegimos un conjunto aleatorio de user_id y traemos TODOS
sus eventos, preservando sesiones (abandono, velocidad) e historial (recurrencia).

Garantías metodológicas:
  - Muestreo ALEATORIO SIMPLE de usuarios (no se sobre-muestrean compradores → no
    sesga las tasas del funnel).
  - Semilla fija (config.SEED) → reproducible.
  - El crudo NO se transforma: esto solo selecciona filas. La limpieza y el feature
    engineering ocurren después, en el EDA (raw es inmutable).

Corre una sola vez:  python src/sampling.py
Salida: data/processed/muestra_usuarios.parquet
"""
import sys
from pathlib import Path

import duckdb

# Permite importar config.py desde la raíz del repo
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

RAW = str(config.RAW_CSV)
OUT = str(config.SAMPLE_PARQUET)
SEED = config.SEED
TARGET_EVENTS = config.TARGET_EVENTS


def main() -> None:
    if not config.RAW_CSV.exists():
        raise FileNotFoundError(
            f"No se encontró el crudo en {RAW}. Descárgalo a data/raw/ antes de correr."
        )
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()  # en memoria; el CSV se lee con streaming

    # ── 1. Conteo para calibrar el número de usuarios ────────────────────────
    print("⏳ Contando eventos y usuarios del crudo (una pasada)...")
    eventos_total, usuarios_total = con.execute(f"""
        SELECT count(*), count(DISTINCT user_id)
        FROM read_csv_auto('{RAW}')
    """).fetchone()

    ev_x_user = eventos_total / usuarios_total
    n_users = round(TARGET_EVENTS / ev_x_user)
    n_users = min(n_users, usuarios_total)  # nunca pedir más usuarios de los que hay

    print(f"   Eventos en el crudo : {eventos_total:,}")
    print(f"   Usuarios únicos     : {usuarios_total:,}")
    print(f"   Eventos por usuario : {ev_x_user:.2f}")
    print(f"   → n_users objetivo  : {n_users:,} (target ≈ {TARGET_EVENTS:,} eventos)")

    # ── 2. Muestra aleatoria simple de user_id (reproducible) ────────────────
    # ORDER BY fija el orden de entrada; reservoir + seed lo hace reproducible.
    print(f"⏳ Muestreando {n_users:,} usuarios (semilla {SEED})...")
    con.execute(f"""
        CREATE TABLE sampled_users AS
        SELECT user_id FROM (
            SELECT DISTINCT user_id FROM read_csv_auto('{RAW}') ORDER BY user_id
        ) USING SAMPLE {n_users} ROWS (reservoir, {SEED});
    """)

    # ── 3. Traer TODOS los eventos de esos usuarios y guardar en Parquet ─────
    print("⏳ Extrayendo todos los eventos de los usuarios muestreados → Parquet...")
    con.execute(f"""
        COPY (
            SELECT e.*
            FROM read_csv_auto('{RAW}') e
            WHERE e.user_id IN (SELECT user_id FROM sampled_users)
        ) TO '{OUT}' (FORMAT PARQUET);
    """)

    # ── 4. Reporte sobre la muestra resultante ───────────────────────────────
    print("\n" + "=" * 60)
    print("RESULTADO DE LA MUESTRA POR USUARIO")
    print("=" * 60)

    tot, n_u, n_s = con.execute(f"""
        SELECT count(*), count(DISTINCT user_id), count(DISTINCT user_session)
        FROM read_parquet('{OUT}')
    """).fetchone()

    print(f"Eventos totales      : {tot:,}")
    print(f"Usuarios             : {n_u:,}")
    print(f"Sesiones             : {n_s:,}")
    print("\nDistribución de event_type:")
    for et, n in con.execute(f"""
        SELECT event_type, count(*) AS n
        FROM read_parquet('{OUT}')
        GROUP BY event_type ORDER BY n DESC
    """).fetchall():
        print(f"   {et:<10} {n:>10,}  ({n / tot * 100:5.2f}%)")

    n_purchase = con.execute(f"""
        SELECT count(*) FROM read_parquet('{OUT}') WHERE event_type = 'purchase'
    """).fetchone()[0]

    print(f"\nEventos purchase     : {n_purchase:,}")
    print(f"\n✅ Muestra guardada en: {OUT}")
    print("Anota en docs/ESTADO_PROYECTO.md: n_users, eventos, purchases y la semilla.")


if __name__ == "__main__":
    main()
