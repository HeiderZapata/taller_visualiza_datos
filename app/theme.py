"""
app/theme.py — Plantilla Plotly y helpers de formato para el dashboard.

Principios del curso aplicados:
  - Data-to-Ink: fondo limpio, sin grillas pesadas ni bordes.
  - Atributo preatentivo de color: gris neutro para el contexto, UN color fuerte (rojo)
    solo para el elemento crítico (electronics / recurrentes / mediana).
  - Jerarquía tipográfica: título oscuro, anotaciones secundarias en gris.
"""
import plotly.graph_objects as go
import plotly.io as pio

# ── Paleta ────────────────────────────────────────────────────────────────────
GREY = "#b0b0b0"    # contexto / "el resto"
CRIT = "#d62728"    # rojo: elemento crítico (lo único que debe saltar a la vista)
ACCENT = "#1f77b4"  # azul de apoyo (compras / valor)
GREEN = "#2ca02c"   # ok / recuperado
DARK = "#2c2c2c"    # texto de títulos
MUTED = "#6b6b6b"   # texto secundario

# ── Plantilla Plotly registrada como "taller" ──────────────────────────────────
_template = go.layout.Template()
_template.layout = go.Layout(
    font=dict(family="Segoe UI, Arial, sans-serif", size=14, color=DARK),
    title=dict(font=dict(size=18, color=DARK), x=0.0, xanchor="left"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    colorway=[ACCENT, CRIT, GREY, GREEN, "#9467bd", "#8c564b"],
    xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="#e0e0e0", ticks="outside", tickcolor="#e0e0e0"),
    yaxis=dict(showgrid=False, zeroline=False, showline=False),
    margin=dict(l=10, r=20, t=60, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    hoverlabel=dict(font_size=13, font_family="Segoe UI, Arial, sans-serif"),
)
pio.templates["taller"] = _template


def base_fig():
    """Devuelve una figura vacía con la plantilla del taller aplicada."""
    fig = go.Figure()
    fig.update_layout(template="taller")
    return fig


# ── Helpers de formato ──────────────────────────────────────────────────────────
def fmt_money(x, decimals=0):
    """Formatea un monto en USD, con separador de miles. Ej: 2076999 -> '$2,076,999'."""
    try:
        return f"${x:,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def fmt_money_short(x):
    """Monto compacto para titulares. Ej: 2076999 -> '$2,08 M' (estilo es-CO)."""
    try:
        if abs(x) >= 1_000_000:
            return f"${x/1_000_000:.2f} M".replace(".", ",")
        if abs(x) >= 1_000:
            return f"${x/1_000:.0f} K"
        return f"${x:,.0f}"
    except (TypeError, ValueError):
        return "—"


def fmt_pct(x, decimals=1):
    """Formatea un porcentaje. Ej: 32.4 -> '32,4%' (coma decimal)."""
    try:
        return f"{x:.{decimals}f}%".replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def fmt_int(x):
    """Entero con separador de miles. Ej: 7511 -> '7,511'."""
    try:
        return f"{int(round(x)):,}"
    except (TypeError, ValueError):
        return "—"
