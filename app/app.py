"""
app/app.py — FASE III: Dashboard analítico (Streamlit) del Taller 2.

Mensaje central D2: "el negocio deja dinero sobre la mesa en electrónica", capturable en
dos momentos — Palanca A (recuperar carritos abandonados, PN1) y Palanca B (retener al
núcleo recurrente, PN2) — con PN3 (cuándo/con qué activar el incentivo).

Diseño: titular-acción FIJO arriba (cifras ancla sobre el df sin filtrar) + KPIs y gráficos
REACTIVOS a los filtros del sidebar. 4 pestañas (Resumen / A / B / Cuándo). Reutiliza
config.py, src/prep.py, src/metrics.py y src/funnel.py.

Ejecutar:  .venv\\Scripts\\python.exe -m streamlit run app/app.py
"""
import sys
from pathlib import Path

import streamlit as st

# Rutas: raíz del repo (para config y src/*) y carpeta app/ (para módulos hermanos).
# OJO: la carpeta se llama 'app' y el script también 'app.py' → para evitar el choque de
# nombres importamos theme/charts como módulos hermanos (no 'from app import ...').
_APP_DIR = Path(__file__).resolve().parent
_ROOT = _APP_DIR.parent
sys.path.append(str(_ROOT))
sys.path.insert(0, str(_APP_DIR))
import config  # noqa: E402
from src import prep, metrics  # noqa: E402
import charts  # noqa: E402
from theme import fmt_money, fmt_money_short, fmt_pct, fmt_int  # noqa: E402

st.set_page_config(page_title="Taller 2 — Incentivos e-commerce", page_icon="💡", layout="wide")

FOCO = "electronics"


# ── Carga de datos (cacheada) ─────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando muestra…")
def load_data():
    return prep.load_sample()


@st.cache_data(show_spinner=False)
def anchors():
    """Cifras ancla de D2, calculadas UNA vez sobre el df SIN filtrar (la 'historia' fija)."""
    df = load_data()
    ab = metrics.abandonment(df)
    rec = metrics.recurrence(df)
    ras = metrics.revenue_at_stake(df)
    ds = metrics.decision_speed(df)
    rt = metrics.repurchase_timing(df)
    return {
        "abandono_global": ab["abandono_global"],
        "conv_global": ab["gf"]["conv_rate"],
        "rev_en_juego_foco": float(ras["prize"].loc[FOCO, "revenue_en_juego"]) if FOCO in ras["prize"].index else 0.0,
        "rev_en_juego_total": ras["total_en_juego"],
        "pct_repeat": rec["pct_repeat"],
        "pct_rev_repeat": rec["pct_rev_repeat"],
        "median_min": ds["median_min"],
        "median_days": rt["median_days"],
        "same_pct": rt["same_pct"],
    }


@st.cache_data(show_spinner=False)
def recurrent_user_ids():
    """user_id con >=2 ocasiones de compra (segmento recurrente), sobre el df completo."""
    df = load_data()
    ub = metrics.recurrence(df)["user_buys"]
    return set(ub.index[ub["ocasiones"] >= 2]), set(ub.index[ub["ocasiones"] == 1])


df = load_data()
A = anchors()
rec_ids, ot_ids = recurrent_user_ids()


# ── Sidebar: filtros (revelación progresiva) ──────────────────────────────────
st.sidebar.header("Filtros")
cats_all = sorted(df["category_main"].dropna().unique())
sel_cats = st.sidebar.multiselect("Categoría", cats_all, default=[],
                                  help="Vacío = todas las categorías")
hr = st.sidebar.slider("Hora del día", 0, 23, (0, 23))

with st.sidebar.expander("Filtros avanzados"):
    top_brands = (df["brand"].value_counts().head(30).index.tolist())
    sel_brands = st.multiselect("Marca (top 30 por volumen)", top_brands, default=[],
                                help="Vacío = todas las marcas")
    seg = st.radio("Segmento de comprador", ["Todos", "Recurrentes", "One-time"], index=0)

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ Ventana = solo octubre 2019 (muestra por usuario, semilla 42). Son señales "
    "sólidas para decidir, no verdades definitivas."
)


# ── Aplicar filtros ───────────────────────────────────────────────────────────
def apply_filters(d):
    m = d["hour"].between(hr[0], hr[1])
    if sel_cats:
        m &= d["category_main"].isin(sel_cats)
    if sel_brands:
        m &= d["brand"].isin(sel_brands)
    if seg == "Recurrentes":
        m &= d["user_id"].isin(rec_ids)
    elif seg == "One-time":
        m &= d["user_id"].isin(ot_ids)
    return d[m]


dff = apply_filters(df)
filtros_activos = bool(sel_cats or sel_brands or seg != "Todos" or hr != (0, 23))


# ── Titular fijo (cifras ancla, NO reaccionan a los filtros) ──────────────────
st.markdown(f"## 💡 El negocio deja dinero sobre la mesa en **{FOCO}**")
st.markdown(
    f"**{fmt_money_short(A['rev_en_juego_foco'])}** en carritos abandonados de {FOCO} esperan recuperación, "
    f"y **{fmt_pct(A['pct_repeat'])}** de los compradores (los recurrentes) ya traen el "
    f"**{fmt_pct(A['pct_rev_repeat'])}** del revenue. Dos palancas, una misma categoría:"
)
c1, c2 = st.columns(2)
c1.success("**Palanca A — antes de comprar:** recuperar carritos abandonados con incentivo "
           "inmediato/en pantalla en la **franja matutina**.")
c2.info("**Palanca B — después de comprar:** nudge de recompra a **24–72 h** en la misma "
        "categoría al núcleo recurrente.")

st.markdown("---")
st.caption("Indicadores (reaccionan a los filtros del sidebar):" if filtros_activos
           else "Indicadores (muestra completa — usa el sidebar para filtrar):")

# KPIs reactivos sobre el df filtrado
k_ab = metrics.abandonment(dff) if len(dff) else None
k_rec = metrics.recurrence(dff) if len(dff) else None
k_ras = metrics.revenue_at_stake(dff) if len(dff) else None
k_ds = metrics.decision_speed(dff) if len(dff) else None

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Revenue en juego", fmt_money_short(k_ras["total_en_juego"]) if k_ras else "—")
m2.metric("Abandono de carrito", fmt_pct(k_ab["abandono_global"]) if k_ab else "—")
m3.metric("Conversión por unidad", fmt_pct(k_ab["gf"]["conv_rate"], 2) if k_ab else "—")
m4.metric("Recurrentes / su revenue",
          f"{fmt_pct(k_rec['pct_repeat'])} / {fmt_pct(k_rec['pct_rev_repeat'])}" if k_rec else "—")
m5.metric("Decisión (mediana)", f"{k_ds['median_min']:.1f} min".replace(".", ",") if k_ds and k_ds["median_min"] == k_ds["median_min"] else "—")

if not len(dff):
    st.warning("Ningún evento cumple los filtros actuales. Ajusta el sidebar.")
    st.stop()


# ── Pestañas ──────────────────────────────────────────────────────────────────
tab_resumen, tab_a, tab_b, tab_cuando = st.tabs(
    ["📊 Resumen", "🅰️ Palanca A — Conversión", "🅱️ Palanca B — Retención", "⏰ Cuándo activar"]
)

# --- Resumen: los dos héroes lado a lado (test de 30 s) ---
with tab_resumen:
    st.markdown(
        "**Contexto:** la conversión vive en 1–3%; el reto es asignar incentivos sin "
        "descontar a quien ya iba a comprar. **Hallazgo:** el dinero perdido y el valor "
        "recurrente se concentran en electrónica. **Acción:** dos palancas en paralelo."
    )
    h1, h2 = st.columns(2)
    with h1:
        st.plotly_chart(charts.hero_revenue_at_stake(k_ras, foco=FOCO), key="hero_a", width="stretch")
    with h2:
        if k_rec and k_rec["repeat"] > 0:
            st.plotly_chart(charts.hero_retention(k_rec), key="hero_b", width="stretch")
        else:
            st.info("Sin compradores recurrentes en el filtro actual (prueba con 'Segmento = Todos').")

# --- Palanca A: PN1 ---
with tab_a:
    st.markdown(
        "#### PN1 — ¿Dónde perdemos conversión y cuánto vale recuperarla?\n"
        f"**Contexto:** de cada producto que llega al carrito, ~1/3 no se compra. "
        f"**Hallazgo:** el abandono ({fmt_pct(k_ab['abandono_global'])}) se concentra en "
        f"electrónica/electrodomésticos. **Traducción:** {fmt_money_short(k_ras['total_en_juego'])} "
        f"en juego, la mayoría en {FOCO}. **Acción:** incentivo de cierre (recordatorio de "
        "carrito, urgencia/stock, financiación) a los carritos abandonados de electrónica."
    )
    ca1, ca2 = st.columns(2)
    with ca1:
        st.plotly_chart(charts.hero_revenue_at_stake(k_ras, foco=FOCO), key="a_revenue", width="stretch")
        st.plotly_chart(charts.funnel_chart(k_ab), key="a_funnel", width="stretch")
    with ca2:
        st.plotly_chart(charts.abandonment_by_category(k_ab), key="a_abandono", width="stretch")
        bm = metrics.brand_mix(dff, foco=FOCO)
        if len(bm["g"]):
            st.plotly_chart(charts.brand_chart(bm), key="a_brand", width="stretch")
        else:
            st.info(f"Sin marcas con suficiente volumen en {FOCO} para el filtro actual.")

# --- Palanca B: PN2 ---
with tab_b:
    rt = metrics.repurchase_timing(dff)
    dias_txt = f"{rt['median_days']:.1f}".replace(".", ",") if rt["median_days"] == rt["median_days"] else "—"
    st.markdown(
        "#### PN2 — ¿Quiénes son los clientes valiosos y cómo retenerlos?\n"
        f"**Contexto:** la mayoría compra una sola vez. **Hallazgo:** el "
        f"{fmt_pct(k_rec['pct_repeat'])} recurrente concentra el {fmt_pct(k_rec['pct_rev_repeat'])} "
        f"del revenue (ticket {fmt_money(k_rec['ticket_repeat'])} vs {fmt_money(k_rec['ticket_one_time'])}). "
        f"**Traducción:** retener a ese núcleo rinde más que captar uno nuevo. **Acción:** "
        f"nudge de recompra a 24–72 h (la 2a compra llega en mediana {dias_txt} días, "
        f"{fmt_pct(rt['same_pct'])} en la misma categoría)."
    )
    cb1, cb2 = st.columns(2)
    with cb1:
        if k_rec["repeat"] > 0:
            st.plotly_chart(charts.hero_retention(k_rec), key="b_hero", width="stretch")
        else:
            st.info("Sin recurrentes en el filtro actual.")
        st.plotly_chart(charts.ticket_chart(k_rec), key="b_ticket", width="stretch")
    with cb2:
        if rt["n_recurrent"] > 0:
            st.plotly_chart(charts.timing_chart(rt), key="b_timing", width="stretch")
        else:
            st.info("Sin pares de recompra en el filtro actual (prueba 'Segmento = Todos').")

# --- Cuándo activar: PN3 ---
with tab_cuando:
    hi = metrics.hourly_intensity(dff)
    pc = metrics.price_vs_conversion(dff)
    peak_h = int(hi["compras_x100_vistas"].idxmax())
    min_txt = f"{k_ds['median_min']:.1f}".replace(".", ",") if k_ds["median_min"] == k_ds["median_min"] else "—"
    st.markdown(
        "#### PN3 — ¿Cuándo y con qué activar el incentivo?\n"
        "**Contexto:** el tráfico pica en la tarde, pero no toda visita tiene la misma "
        "intención. **Hallazgo:** la mañana convierte ~2× por visita (pico de intensidad a "
        f"las {peak_h}h) y el comprador con intención decide en {min_txt} min. "
        "**Traducción:** el momento y el tipo de incentivo importan más que el precio. "
        "**Acción:** activar en la franja matutina (6–10 h), incentivo inmediato/en "
        "pantalla; el precio NO es el freno."
    )
    st.plotly_chart(charts.hourly_intensity_chart(hi), key="c_hourly", width="stretch")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.plotly_chart(charts.decision_speed_chart(k_ds), key="c_speed", width="stretch")
    with cc2:
        if len(pc):
            st.plotly_chart(charts.price_vs_conversion_chart(pc, foco=FOCO), key="c_price", width="stretch")
        else:
            st.info("No hay categorías con ≥500 unidades en el filtro actual.")
