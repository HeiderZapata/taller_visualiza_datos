"""
src/funnel.py — A1: funnel por UNIDAD (producto dentro de sesión).

Reemplaza el funnel viejo que dividía CONTEOS DE EVENTOS (purchase_events / view_events),
lo cual NO es un funnel de unidades (el denominador se infla con multi-vistas y las tasas
no encadenan). Aquí la unidad es el par (user_session, product_id): cada producto-en-sesión
se clasifica por su ETAPA MÁS PROFUNDA (view < cart < purchase) y las tasas se ENCADENAN
(de las unidades que llegan a carrito, cuántas terminan en compra).

Lo usan el notebook (sección 4.1) y el dashboard, para que ambos reporten lo mismo.
"""
import pandas as pd

UNIT = ["user_session", "product_id"]


def _unit_flags(df, unit=UNIT, extra_cols=None):
    """Una fila por unidad con banderas has_view / has_cart / has_purchase.

    extra_cols: columnas funcionalmente dependientes de la unidad (p. ej. category_main,
    determinada por product_id) que se incluyen en la clave de agrupación para arrastrarlas.
    """
    cols = [*unit, "event_type"] + (extra_cols or [])
    d = df[cols].copy()
    d["is_view"] = d["event_type"].eq("view")
    d["is_cart"] = d["event_type"].eq("cart")
    d["is_purchase"] = d["event_type"].eq("purchase")
    keys = unit + (extra_cols or [])
    u = d.groupby(keys, observed=True).agg(
        has_view=("is_view", "any"),
        has_cart=("is_cart", "any"),
        has_purchase=("is_purchase", "any"),
    )
    return u


def global_funnel(df, unit=UNIT):
    """Funnel global por unidad. Devuelve conteos, partición por etapa más profunda
    (view_only / cart_only / purchased; suma = n_units) y tasas encadenadas."""
    u = _unit_flags(df, unit)
    n = len(u)
    reached_cart = int((u["has_cart"] | u["has_purchase"]).sum())  # llegó al menos a carrito
    reached_purchase = int(u["has_purchase"].sum())

    purchased = reached_purchase
    cart_only = int((u["has_cart"] & ~u["has_purchase"]).sum())
    view_only = int((u["has_view"] & ~u["has_cart"] & ~u["has_purchase"]).sum())

    return {
        "n_units": n,
        "reached_view": int(u["has_view"].sum()),
        "reached_cart": reached_cart,
        "reached_purchase": reached_purchase,
        "view_only": view_only,
        "cart_only": cart_only,
        "purchased": purchased,
        "cart_rate": reached_cart / n * 100,          # % de unidades que llegan a carrito
        "conv_rate": reached_purchase / n * 100,      # % de unidades que compran
        "cart_to_purchase": (reached_purchase / reached_cart * 100) if reached_cart else float("nan"),
    }


def category_funnel(df, category_col="category_main", min_units=500, unit=UNIT):
    """Funnel por categoría a nivel unidad. Filtra categorías con < min_units unidades
    (para que las tasas sean representativas) y ordena por conv_rate desc."""
    d = df[df[category_col].notna()]
    u = _unit_flags(d, unit, extra_cols=[category_col]).reset_index()
    u["reached_cart"] = u["has_cart"] | u["has_purchase"]

    out = u.groupby(category_col, observed=True).agg(
        units=("has_purchase", "size"),
        reached_cart=("reached_cart", "sum"),
        purchased=("has_purchase", "sum"),
    )
    out["cart_rate"] = out["reached_cart"] / out["units"] * 100
    out["conv_rate"] = out["purchased"] / out["units"] * 100
    out["cart_to_purchase"] = out["purchased"] / out["reached_cart"] * 100

    return out[out["units"] >= min_units].sort_values("conv_rate", ascending=False)
