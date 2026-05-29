"""
app/charts.py — Figuras Plotly del dashboard (Fase III).

Cada función recibe los agregados de src.metrics y devuelve un go.Figure listo para
st.plotly_chart. Reconstruye en Plotly nativo los héroes A y B de la Fase II (no incrusta
los PNG de matplotlib) y el resto de gráficos de soporte. Aplica la plantilla 'taller'
(gris para contexto, rojo solo para lo crítico).
"""
import sys
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app import theme  # noqa: E402
from app.theme import GREY, CRIT, ACCENT, GREEN, MUTED, fmt_money, fmt_money_short, fmt_pct, fmt_int  # noqa: E402


# ── Héroe A (PN1): revenue en juego por categoría ─────────────────────────────
def hero_revenue_at_stake(ras, foco="electronics"):
    """Barras horizontales del revenue abandonado por categoría; foco resaltado en rojo."""
    prize = ras["prize"].sort_values("revenue_en_juego")  # menor->mayor (mayor arriba en barh)
    cats = list(prize.index)
    vals = prize["revenue_en_juego"].tolist()
    colors = [CRIT if c == foco else GREY for c in cats]

    fig = theme.base_fig()
    fig.add_bar(
        x=vals, y=cats, orientation="h", marker_color=colors,
        text=[fmt_money_short(v) for v in vals], textposition="outside",
        hovertemplate="%{y}: %{x:$,.0f} en juego<extra></extra>",
    )
    top = prize["revenue_en_juego"].max()
    fig.update_layout(
        title="Dónde se queda el dinero: carritos abandonados por categoría",
        xaxis_title="Revenue en juego (USD)", yaxis_title=None,
        xaxis_range=[0, top * 1.18], height=420, showlegend=False,
    )
    if foco in prize.index:
        fig.add_annotation(
            x=prize.loc[foco, "revenue_en_juego"], y=foco,
            text="82% del premio total<br>se concentra aquí",
            showarrow=True, arrowhead=2, arrowcolor=CRIT, ax=-90, ay=-30,
            font=dict(color=CRIT, size=12), align="left",
        )
    return fig


# ── Héroe B (PN2): concentración de valor de los recurrentes ──────────────────
def hero_retention(rec):
    """Dos barras 100% apiladas: el 31,7% de compradores (recurrentes) = 69% del revenue."""
    pct_rep = rec["pct_repeat"]
    pct_ot = 100 - pct_rep
    pct_rev_rep = rec["pct_rev_repeat"]
    pct_rev_ot = 100 - pct_rev_rep
    x = ["Compradores", "Revenue"]

    fig = theme.base_fig()
    fig.add_bar(
        name="Recurrentes (≥2 compras)", x=x, y=[pct_rep, pct_rev_rep],
        marker_color=CRIT,
        text=[fmt_pct(pct_rep), fmt_pct(pct_rev_rep)], textposition="inside",
        insidetextfont=dict(color="white", size=15),
        hovertemplate="Recurrentes: %{y:.1f}%<extra></extra>",
    )
    fig.add_bar(
        name="One-time (1 compra)", x=x, y=[pct_ot, pct_rev_ot],
        marker_color=GREY,
        text=[fmt_pct(pct_ot), fmt_pct(pct_rev_ot)], textposition="inside",
        insidetextfont=dict(color=MUTED, size=13),
        hovertemplate="One-time: %{y:.1f}%<extra></extra>",
    )
    fig.update_layout(
        barmode="stack", title="El mismo grupo: 1 de cada 3 compradores trae 7 de cada 10 dólares",
        yaxis=dict(title="% del total", range=[0, 100], ticksuffix="%"),
        height=420, legend=dict(orientation="h", y=1.08, x=0),
    )
    fig.add_annotation(
        x=0, y=pct_rep / 2, ax=1, ay=pct_rev_rep / 2, xref="x", yref="y", axref="x", ayref="y",
        text="", showarrow=True, arrowhead=2, arrowcolor=CRIT, arrowwidth=2,
    )
    return fig


# ── Funnel por unidad (PN1) ───────────────────────────────────────────────────
def funnel_chart(ab):
    """Funnel por unidad (producto-en-sesión): vistas -> carrito -> compra."""
    gf = ab["gf"]
    fig = theme.base_fig()
    fig.add_trace(go.Funnel(
        y=["Vista", "Llega al carrito", "Compra"],
        x=[gf["n_units"], gf["reached_cart"], gf["reached_purchase"]],
        textinfo="value+percent initial",
        marker_color=[GREY, ACCENT, CRIT],
        hovertemplate="%{y}: %{x:,} unidades<extra></extra>",
    ))
    fig.update_layout(
        title=f"Funnel por unidad — solo el {fmt_pct(gf['conv_rate'],2)} de los productos vistos se compra",
        height=380, showlegend=False,
    )
    return fig


# ── Abandono por categoría (PN1) ──────────────────────────────────────────────
def abandonment_by_category(ab, foco=("electronics", "computers")):
    """Tasa de abandono por categoría, anotada con el volumen de carritos abandonados."""
    aband_cat = ab["aband_cat"].sort_values("abandono")
    cats = list(aband_cat.index)
    vals = aband_cat["abandono"].tolist()
    vols = aband_cat["abandonados"].tolist()
    colors = [CRIT if c in foco else GREY for c in cats]

    fig = theme.base_fig()
    fig.add_bar(
        x=vals, y=cats, orientation="h", marker_color=colors,
        text=[f"{fmt_int(v)} carritos" for v in vols], textposition="outside",
        hovertemplate="%{y}: %{x:.1f}% abandono<extra></extra>",
    )
    g = ab["abandono_global"]
    fig.add_vline(x=g, line_dash="dash", line_color=CRIT,
                  annotation_text=f"Global {fmt_pct(g)}", annotation_position="top")
    fig.update_layout(
        title="Abandono de carrito por categoría (% que llega al carrito y no compra)",
        xaxis_title="% de abandono", yaxis_title=None,
        xaxis_range=[0, max(vals) * 1.25], height=420, showlegend=False,
    )
    return fig


# ── Marca dentro de electronics (PN1) ─────────────────────────────────────────
def brand_chart(bm, top_n=8):
    """Carritos por marca dentro de la categoría foco (abandonados vs comprados)."""
    g = bm["g"].sort_values("carritos", ascending=False).head(top_n).iloc[::-1]
    fig = theme.base_fig()
    fig.add_bar(name="Abandonados", x=g["abandonados"], y=g.index, orientation="h", marker_color=CRIT,
                hovertemplate="%{y}: %{x:,} abandonados<extra></extra>")
    fig.add_bar(name="Comprados", x=g["comprados"], y=g.index, orientation="h", marker_color=GREEN,
                hovertemplate="%{y}: %{x:,} comprados<extra></extra>")
    fig.update_layout(
        barmode="stack",
        title=f"Marcas en {bm['foco']}: dónde están los carritos (y cuántos se pierden)",
        xaxis_title="Carritos (unidades producto-en-sesión)", yaxis_title=None,
        height=420, legend=dict(orientation="h", y=1.08, x=0),
    )
    return fig


# ── Timing de recompra (PN2) ──────────────────────────────────────────────────
def timing_chart(rt, cap_days=30):
    """Distribución de días entre la 1a y la 2a compra (cap en la ventana de octubre)."""
    days = rt["days"]
    days = days[days <= cap_days]
    fig = theme.base_fig()
    fig.add_histogram(x=days, nbinsx=30, marker_color=ACCENT,
                      hovertemplate="%{x:.0f} días: %{y} usuarios<extra></extra>")
    med = rt["median_days"]
    fig.add_vline(x=med, line_dash="dash", line_color=CRIT,
                  annotation_text=f"Mediana {med:.1f} días".replace(".", ","),
                  annotation_position="top")
    fig.update_layout(
        title="¿Cuándo vuelve el comprador? Días entre la 1a y la 2a compra",
        xaxis_title="Días hasta la 2a compra (ventana octubre)", yaxis_title="Usuarios recurrentes",
        height=380, showlegend=False,
    )
    return fig


# ── Ticket por segmento (PN2) ─────────────────────────────────────────────────
def ticket_chart(rec):
    """Ticket promedio one-time vs recurrente (≈5×)."""
    fig = theme.base_fig()
    vals = [rec["ticket_one_time"], rec["ticket_repeat"]]
    fig.add_bar(
        x=["One-time", "Recurrente"], y=vals, marker_color=[GREY, CRIT],
        text=[fmt_money(v) for v in vals], textposition="outside",
        hovertemplate="%{x}: %{y:$,.0f}<extra></extra>",
    )
    fig.update_layout(
        title="Ticket promedio: el recurrente vale ~5× más",
        yaxis_title="USD por comprador", xaxis_title=None,
        yaxis_range=[0, max(vals) * 1.2], height=380, showlegend=False,
    )
    return fig


# ── Intensidad horaria (PN3) ──────────────────────────────────────────────────
def hourly_intensity_chart(hi):
    """Dos paneles: distribución horaria normalizada (izq) e intensidad de compra (der)."""
    horas = list(hi.index)
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Distribución por hora (normalizada por tipo)",
                        "Intensidad: compras por 100 vistas"),
    )
    # Panel izq: distribución normalizada
    fig.add_scatter(x=horas, y=hi["%_vistas"], name="Vistas", line=dict(color=GREY, width=2),
                    mode="lines+markers", row=1, col=1)
    fig.add_scatter(x=horas, y=hi["%_carritos"], name="Carritos", line=dict(color=ACCENT, width=2),
                    mode="lines+markers", row=1, col=1)
    fig.add_scatter(x=horas, y=hi["%_compras"], name="Compras", line=dict(color=CRIT, width=3),
                    mode="lines+markers", row=1, col=1)
    # Panel der: intensidad
    peak_h = int(hi["compras_x100_vistas"].idxmax())
    bar_colors = [CRIT if h == peak_h else GREY for h in horas]
    fig.add_bar(x=horas, y=hi["compras_x100_vistas"], marker_color=bar_colors, showlegend=False,
                hovertemplate="%{x}h: %{y:.2f} compras/100 vistas<extra></extra>", row=1, col=2)

    fig.update_xaxes(title_text="Hora del día", row=1, col=1)
    fig.update_xaxes(title_text="Hora del día", row=1, col=2)
    fig.update_yaxes(title_text="% de sus eventos", row=1, col=1)
    fig.update_yaxes(title_text="Compras por 100 vistas", row=1, col=2)
    fig.update_layout(
        template="taller", height=420,
        title="La mañana decide: pico de compra a las 7h y ~2× de intensidad por visita",
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig


# ── Velocidad de decisión (PN3) ───────────────────────────────────────────────
def decision_speed_chart(ds, cap_min=30):
    """Distribución del tiempo de decisión (minutos), cap para legibilidad."""
    dt = ds["decision_time"]
    dt = dt[dt <= cap_min]
    fig = theme.base_fig()
    fig.add_histogram(x=dt, nbinsx=30, marker_color=ACCENT,
                      hovertemplate="%{x:.0f} min: %{y} unidades<extra></extra>")
    med = ds["median_min"]
    fig.add_vline(x=med, line_dash="dash", line_color=CRIT,
                  annotation_text=f"Mediana {med:.1f} min".replace(".", ","),
                  annotation_position="top")
    fig.update_layout(
        title=f"Decisión en minutos: {fmt_pct(ds['pct_lt5'])} compra en <5 min",
        xaxis_title="Minutos del 1er view a la compra (≤30 min)", yaxis_title="Unidades",
        height=380, showlegend=False,
    )
    return fig


# ── Precio vs conversión (PN3) ────────────────────────────────────────────────
def price_vs_conversion_chart(pc, foco="electronics"):
    """Scatter precio mediana por categoría vs conversión; el precio no es el freno."""
    cats = list(pc.index)
    colors = [CRIT if c == foco else GREY for c in cats]
    fig = theme.base_fig()
    fig.add_scatter(
        x=pc["precio_mediana"], y=pc["conv_rate"], mode="markers+text",
        text=cats, textposition="top center", textfont=dict(size=11, color=MUTED),
        marker=dict(size=12, color=colors),
        hovertemplate="%{text}<br>precio mediana %{x:$,.0f}<br>conv %{y:.2f}%<extra></extra>",
    )
    fig.update_layout(
        title="El precio no es el freno: las categorías baratas convierten peor, no mejor",
        xaxis_title="Precio mediana por producto (USD)", yaxis_title="Conversión por unidad (%)",
        height=420, showlegend=False,
    )
    return fig
