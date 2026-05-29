"""
src/metrics.py — FASE III: métricas del EDA portadas a funciones puras y reutilizables.

Cada función recibe el DataFrame YA limpio (de src.prep.load_sample) y, en el dashboard,
YA filtrado por el sidebar. Las fórmulas son IDÉNTICAS a las del notebook (Fase I) para que
dashboard y EDA reporten lo mismo. Reutiliza src/funnel.py para el funnel por unidad.

Mapa función -> sección del notebook:
  recurrence          -> 4.6 (recurrencia por ocasión)
  abandonment         -> 4.5 (abandono por unidad; reusa funnel.py)
  revenue_at_stake    -> 4.8a (premio en $ de carritos abandonados)
  repurchase_timing   -> 4.8b (días a la 2a compra + misma categoría)
  brand_mix           -> 4.8c (marca dentro de electronics)
  hourly_intensity    -> 4.3 (distribución horaria + compras por 100 vistas)
  decision_speed      -> 4.7 (velocidad de decisión por producto-en-sesión)
  price_vs_conversion -> 4.2 (precio por producto único vs conversión)
"""
import sys
from pathlib import Path

import pandas as pd

# Raíz del repo en sys.path para importar funnel (mismo patrón que el notebook)
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.funnel import global_funnel, category_funnel  # noqa: E402


# ── 4.6 Recurrencia (por ocasión) ─────────────────────────────────────────────
def recurrence(df):
    """Segmenta compradores en one-time vs recurrentes (ocasión = sesión con compra)."""
    purchases = df[df["event_type"] == "purchase"]
    user_buys = purchases.groupby("user_id").agg(
        ocasiones=("user_session", "nunique"),  # sesiones distintas con compra
        items=("event_type", "size"),           # eventos purchase (ítems comprados)
        revenue=("price", "sum"),
    )

    one_time = int((user_buys["ocasiones"] == 1).sum())
    repeat = int((user_buys["ocasiones"] >= 2).sum())
    n_buyers = one_time + repeat
    rev_one_time = float(user_buys.loc[user_buys["ocasiones"] == 1, "revenue"].sum())
    rev_repeat = float(user_buys.loc[user_buys["ocasiones"] >= 2, "revenue"].sum())
    rev_total = float(user_buys["revenue"].sum())

    return {
        "user_buys": user_buys,
        "one_time": one_time,
        "repeat": repeat,
        "n_buyers": n_buyers,
        "rev_one_time": rev_one_time,
        "rev_repeat": rev_repeat,
        "rev_total": rev_total,
        "pct_repeat": repeat / n_buyers * 100 if n_buyers else float("nan"),
        "pct_rev_repeat": rev_repeat / rev_total * 100 if rev_total else float("nan"),
        "ticket_one_time": rev_one_time / one_time if one_time else float("nan"),
        "ticket_repeat": rev_repeat / repeat if repeat else float("nan"),
    }


# ── 4.5 Abandono de carrito (por unidad) ──────────────────────────────────────
def abandonment(df, min_units=500):
    """Abandono por unidad (producto-en-sesión), global y por categoría. Reusa funnel.py."""
    gf = global_funnel(df)
    cat_funnel = category_funnel(df, min_units=min_units)
    abandono_global = 100 - gf["cart_to_purchase"]
    aband_cat = cat_funnel.assign(
        abandonados=(cat_funnel["reached_cart"] - cat_funnel["purchased"]),
        abandono=100 - cat_funnel["cart_to_purchase"],
    ).sort_values("abandono", ascending=False)
    return {
        "gf": gf,
        "cat_funnel": cat_funnel,
        "abandono_global": abandono_global,
        "aband_cat": aband_cat,
    }


# ── 4.8a Revenue en juego (carritos abandonados) ──────────────────────────────
def revenue_at_stake(df, recovery_rates=(0.05, 0.10, 0.20)):
    """Revenue perdido en carritos abandonados por categoría + escenarios de recuperación."""
    ev = df.copy()
    ev["is_cart"] = ev["event_type"].eq("cart")
    ev["is_purchase"] = ev["event_type"].eq("purchase")
    unit = ev.groupby(["user_session", "product_id"], observed=True).agg(
        has_cart=("is_cart", "any"),
        has_purchase=("is_purchase", "any"),
        price=("price", "median"),
        category_main=("category_main", "first"),
    )
    aband = unit[unit["has_cart"] & ~unit["has_purchase"]]

    prize = (
        aband.groupby("category_main", observed=True)["price"]
        .agg(carritos="size", revenue_en_juego="sum")
    )
    prize["ticket_medio"] = prize["revenue_en_juego"] / prize["carritos"]
    prize = prize.sort_values("revenue_en_juego", ascending=False)

    top_cat = prize.index[0] if len(prize) else None
    scenarios = (
        {r: float(prize.loc[top_cat, "revenue_en_juego"] * r) for r in recovery_rates}
        if top_cat is not None
        else {}
    )
    return {
        "aband": aband,
        "prize": prize,
        "total_en_juego": float(aband["price"].sum()),
        "n_carritos": int(len(aband)),
        "top_cat": top_cat,
        "scenarios": scenarios,
    }


# ── 4.8b Timing de recompra ───────────────────────────────────────────────────
def repurchase_timing(df):
    """Días entre la 1a y la 2a ocasión de compra + % de 2a compra en la misma categoría."""
    purch = df[df["event_type"] == "purchase"]
    occ = (
        purch.groupby(["user_id", "user_session"])
        .agg(
            t=("event_time", "min"),
            category=(
                "category_main",
                lambda s: s.dropna().mode().iloc[0] if s.dropna().size else pd.NA,
            ),
        )
        .reset_index()
        .sort_values(["user_id", "t"])
    )
    occ["rank"] = occ.groupby("user_id").cumcount() + 1

    first = occ[occ["rank"] == 1].set_index("user_id")[["t", "category"]]
    second = occ[occ["rank"] == 2].set_index("user_id")[["t", "category"]]
    pair = first.join(second, lsuffix="_1", rsuffix="_2", how="inner")  # usuarios con >=2 ocasiones
    days = (pair["t_2"] - pair["t_1"]).dt.total_seconds() / 86400

    cat_pair = pair.dropna(subset=["category_1", "category_2"])
    same = (
        float((cat_pair["category_1"] == cat_pair["category_2"]).mean() * 100)
        if len(cat_pair)
        else float("nan")
    )
    return {
        "pair": pair,
        "days": days,
        "same_pct": same,
        "median_days": float(days.median()) if len(days) else float("nan"),
        "n_recurrent": int(len(pair)),
        "n_cat_pairs": int(len(cat_pair)),
    }


# ── 4.8c Marca dentro de electronics ──────────────────────────────────────────
def brand_mix(df, foco="electronics", min_carritos=100):
    """Reparto de carritos (y abandono) por marca dentro de la categoría foco."""
    evf = df[df["category_main"] == foco].copy()
    evf["is_cart"] = evf["event_type"].eq("cart")
    evf["is_purchase"] = evf["event_type"].eq("purchase")
    u = (
        evf.groupby(["user_session", "product_id"], observed=True)
        .agg(
            has_cart=("is_cart", "any"),
            has_purchase=("is_purchase", "any"),
            brand=("brand", "first"),
            price=("price", "median"),
        )
        .reset_index()
    )
    u["reached_cart"] = u["has_cart"] | u["has_purchase"]
    carted = u[u["reached_cart"]]

    n_total = int(len(carted))
    n_nulos = int(carted["brand"].isna().sum())

    g = (
        carted.dropna(subset=["brand"])
        .groupby("brand", observed=True)
        .agg(
            carritos=("reached_cart", "size"),
            comprados=("has_purchase", "sum"),
            ticket=("price", "median"),
        )
    )
    g["abandonados"] = g["carritos"] - g["comprados"]
    g["abandono_%"] = (g["abandonados"] / g["carritos"] * 100).round(1)
    g = g[g["carritos"] >= min_carritos].sort_values("abandonados", ascending=False)
    return {"g": g, "n_total": n_total, "n_nulos": n_nulos, "foco": foco}


# ── 4.3 Intensidad horaria ────────────────────────────────────────────────────
def hourly_intensity(df):
    """Distribución horaria por tipo de evento + intensidad (compras por 100 vistas)."""
    hora_tab = (
        df.groupby(["hour", "event_type"]).size()
        .unstack(fill_value=0)
        .reindex(columns=["view", "cart", "purchase"], fill_value=0)
    )
    hora_tab.columns = ["views", "carts", "purchases"]

    hora_tab["%_vistas"] = (hora_tab["views"] / hora_tab["views"].sum() * 100).round(2)
    hora_tab["%_carritos"] = (hora_tab["carts"] / hora_tab["carts"].sum() * 100).round(2)
    hora_tab["%_compras"] = (hora_tab["purchases"] / hora_tab["purchases"].sum() * 100).round(2)
    hora_tab["compras_x100_vistas"] = (hora_tab["purchases"] / hora_tab["views"] * 100).round(2)
    return hora_tab


# ── 4.7 Velocidad de decisión ─────────────────────────────────────────────────
def decision_speed(df):
    """Minutos del primer view del producto a su compra, por producto-en-sesión."""
    ev = df.sort_values("event_time")
    first_view = (
        ev[ev["event_type"] == "view"]
        .groupby(["user_session", "product_id"])["event_time"].min()
        .rename("first_view")
    )
    purchase_time = (
        ev[ev["event_type"] == "purchase"]
        .groupby(["user_session", "product_id"])["event_time"].min()
        .rename("purchase_time")
    )
    decisiones = pd.concat([first_view, purchase_time], axis=1).dropna()
    decision_time = (
        (decisiones["purchase_time"] - decisiones["first_view"]).dt.total_seconds() / 60
    )

    n_neg = int((decision_time < 0).sum())
    decision_time = decision_time[decision_time >= 0]  # descartar artefactos negativos

    has = len(decision_time) > 0
    return {
        "decision_time": decision_time,
        "n_neg": n_neg,
        "n_units": int(len(decisiones)),
        "median_min": float(decision_time.median()) if has else float("nan"),
        "pct_lt5": float((decision_time < 5).mean() * 100) if has else float("nan"),
        "pct_lt10": float((decision_time < 10).mean() * 100) if has else float("nan"),
        "pct_lt30": float((decision_time < 30).mean() * 100) if has else float("nan"),
    }


# ── 4.2 Precio vs conversión ──────────────────────────────────────────────────
def price_vs_conversion(df, min_units=500):
    """Precio por producto único (agregado por categoría) cruzado con conv_rate (>=min_units)."""
    prod_precio = (
        df[df["category_main"].notna()]
        .groupby(["category_main", "product_id"])["price"]
        .median()
    )
    precio_cat = (
        prod_precio.groupby("category_main")
        .agg(precio_promedio="mean", precio_mediana="median", n_productos="count")
        .round(2)
    )
    cat_funnel = category_funnel(df, min_units=min_units)
    precio_conv = (
        cat_funnel[["units", "purchased", "cart_rate", "conv_rate"]]
        .join(precio_cat[["precio_promedio", "precio_mediana"]], how="inner")
        .sort_values("conv_rate", ascending=False)
    )
    return precio_conv
