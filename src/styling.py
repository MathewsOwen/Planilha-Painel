"""Tema visual do painel: cores vindas de branding.THEME."""

from branding import THEME

THEME_BLUE = THEME["blue"]
THEME_BLUE_DARK = THEME["blue_dark"]
THEME_BLUE_MEDIUM = THEME["blue_medium"]
THEME_BLUE_LIGHT = THEME["blue_light"]
THEME_BLUE_ACCENT = THEME["blue_accent"]
THEME_YELLOW = THEME["yellow"]
THEME_RED = "#c0392b"
THEME_GREEN = "#2f855a"

WHITE = "#ffffff"
OFF_WHITE = "#f4f7fb"
LIGHT_BORDER = "#dde5f0"
TEXT_PRIMARY = THEME["text_primary"]
TEXT_SECONDARY = "#5a6b85"
TEXT_TERTIARY = "#94a3b8"

CID_COLORS = {
    "F30-F39": THEME_BLUE_MEDIUM,
    "F40-F49": THEME_BLUE_LIGHT,
    "F20-F29": THEME_BLUE_DARK,
    "F60-F69": "#7c5cbf",
    "F00-F09": "#6b7280",
    "F10-F19": "#9b6b3f",
    "F50-F59": THEME_YELLOW,
    "F90-F98": THEME_GREEN,
}

RISK_COLORS = {
    "CRÍTICO": THEME_RED,
    "ALTO": "#dd6b20",
    "MÉDIO": THEME_YELLOW,
    "BAIXO": THEME_GREEN,
}

CUSTOM_CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

  html, body, [data-testid="stAppViewContainer"] {{
    background: {OFF_WHITE} !important;
    color: {TEXT_PRIMARY};
    font-family: 'Inter', sans-serif;
  }}

  [data-testid="stHeader"] {{ background: transparent; }}
  [data-testid="stToolbar"] {{ right: 1rem; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {THEME_BLUE} 0%, {THEME_BLUE_DARK} 100%);
  }}
  [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
    color: #ffffff !important;
    font-family: 'Sora', sans-serif;
  }}
  [data-testid="stSidebar"] label {{
    color: #cfdaf0 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] input,
  [data-testid="stSidebar"] [data-baseweb="input"] > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
  }}

  /* Header principal */
  .app-header {{
    background: linear-gradient(135deg, {THEME_BLUE} 0%, {THEME_BLUE_MEDIUM} 100%);
    color: #ffffff;
    padding: 32px 36px;
    border-radius: 18px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    box-shadow: 0 8px 30px rgba(10,44,91,0.15);
    position: relative;
    overflow: hidden;
  }}
  .app-header::after {{
    content: '';
    position: absolute;
    right: -60px; top: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
  }}
  .app-header h1 {{
    font-family: 'Sora', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
  }}
  .app-header p {{
    color: #cfdaf0;
    font-size: 0.92rem;
    font-weight: 400;
    margin: 0;
  }}
  .app-badge {{
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 12px;
    display: inline-block;
  }}
  .app-period {{
    font-family: 'Sora', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
  }}
  .app-period-sub {{ color: #cfdaf0; font-size: 0.78rem; margin-top: 4px; }}

  /* KPI Cards */
  .kpi-card {{
    background: {WHITE};
    border: 1px solid {LIGHT_BORDER};
    border-radius: 16px;
    padding: 22px 22px 20px 22px;
    box-shadow: 0 2px 12px rgba(10,44,91,0.04);
    height: 100%;
    transition: transform 0.18s, box-shadow 0.18s;
    position: relative;
    overflow: hidden;
  }}
  .kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(10,44,91,0.1);
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: {THEME_BLUE_MEDIUM};
  }}
  .kpi-card.warn::before {{ background: {THEME_YELLOW}; }}
  .kpi-card.danger::before {{ background: {THEME_RED}; }}
  .kpi-card.success::before {{ background: {THEME_GREEN}; }}
  .kpi-card.accent::before {{ background: {THEME_BLUE_LIGHT}; }}
  .kpi-label {{
    font-size: 0.7rem;
    color: {TEXT_SECONDARY};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin-bottom: 10px;
  }}
  .kpi-value {{
    font-family: 'Sora', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: {THEME_BLUE};
    line-height: 1;
    letter-spacing: -0.02em;
  }}
  .kpi-card.warn .kpi-value {{ color: {THEME_YELLOW}; }}
  .kpi-card.danger .kpi-value {{ color: {THEME_RED}; }}
  .kpi-card.success .kpi-value {{ color: {THEME_GREEN}; }}
  .kpi-card.accent .kpi-value {{ color: {THEME_BLUE_LIGHT}; }}
  .kpi-sub {{ font-size: 0.75rem; color: {TEXT_SECONDARY}; margin-top: 6px; }}

  /* Section title */
  .section-title {{
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {THEME_BLUE};
    margin: 28px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .section-title::before {{
    content: '';
    width: 6px;
    height: 18px;
    background: {THEME_BLUE_MEDIUM};
    border-radius: 3px;
  }}

  /* Insight box */
  .insight-box {{
    background: linear-gradient(135deg, rgba(10,44,91,0.04) 0%, rgba(29,79,145,0.06) 100%);
    border: 1px solid rgba(29,79,145,0.18);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
  }}
  .insight-num {{
    font-family: 'Sora', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: {THEME_BLUE};
  }}
  .insight-label {{
    font-size: 0.8rem;
    color: {TEXT_SECONDARY};
    margin-top: 4px;
    line-height: 1.5;
  }}

  /* Generic card */
  .card-app {{
    background: {WHITE};
    border: 1px solid {LIGHT_BORDER};
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 2px 10px rgba(10,44,91,0.03);
    margin-bottom: 18px;
  }}
  .card-title {{
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: {THEME_BLUE};
    margin: 0 0 18px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid {LIGHT_BORDER};
  }}

  /* Cidade rank rows */
  .city-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border: 1px solid {LIGHT_BORDER};
    border-left: 3px solid {THEME_BLUE_MEDIUM};
    border-radius: 10px;
    margin-bottom: 10px;
    background: {WHITE};
  }}
  .city-row.critico {{ border-left-color: {THEME_RED}; background: linear-gradient(90deg, rgba(192,57,43,0.05), {WHITE}); }}
  .city-row.alto    {{ border-left-color: #dd6b20; background: linear-gradient(90deg, rgba(221,107,32,0.05), {WHITE}); }}
  .city-row.medio   {{ border-left-color: {THEME_YELLOW}; }}
  .city-row.baixo   {{ border-left-color: {THEME_GREEN}; background: linear-gradient(90deg, rgba(47,133,90,0.04), {WHITE}); }}

  .city-rank {{
    font-family: 'Sora', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: {TEXT_TERTIARY};
    width: 32px;
    text-align: center;
  }}
  .city-name {{
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: {THEME_BLUE};
  }}
  .city-meta {{ font-size: 0.74rem; color: {TEXT_SECONDARY}; margin-top: 3px; }}
  .city-pill {{
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .pill-critico {{ background: rgba(192,57,43,0.12); color: {THEME_RED}; }}
  .pill-alto    {{ background: rgba(221,107,32,0.12); color: #dd6b20; }}
  .pill-medio   {{ background: rgba(244,185,66,0.18); color: #b8801c; }}
  .pill-baixo   {{ background: rgba(47,133,90,0.12); color: {THEME_GREEN}; }}

  /* Plan card */
  .plan-card {{
    background: {WHITE};
    border: 1px solid {LIGHT_BORDER};
    border-radius: 14px;
    padding: 22px;
    height: 100%;
    transition: transform 0.18s, box-shadow 0.18s;
    border-top: 3px solid {THEME_BLUE_MEDIUM};
  }}
  .plan-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(10,44,91,0.08);
  }}
  .plan-icon {{ font-size: 1.6rem; margin-bottom: 8px; }}
  .plan-title {{
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: {THEME_BLUE};
    margin-bottom: 6px;
  }}
  .plan-desc {{ font-size: 0.78rem; color: {TEXT_SECONDARY}; line-height: 1.6; }}
  .plan-tag {{
    display: inline-block;
    margin-top: 10px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 10px;
    background: rgba(29,79,145,0.1);
    color: {THEME_BLUE_MEDIUM};
  }}

  /* Conclusion */
  .conclusion-card {{
    background: linear-gradient(135deg, {THEME_BLUE} 0%, {THEME_BLUE_DARK} 100%);
    color: #ffffff;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 24px;
  }}
  .conclusion-card .col-title {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    color: #f4b942;
    margin-bottom: 8px;
  }}
  .conclusion-card .col-text {{
    font-size: 0.84rem;
    line-height: 1.7;
    color: #e2eaf7;
  }}
  .conclusion-card strong {{ color: #ffffff; }}

  /* Hide Streamlit chrome */
  #MainMenu, footer {{ visibility: hidden; }}

  /* Reduce default padding */
  .main .block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }}
  thead th {{
    text-align: left;
    padding: 10px 14px;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 2px solid {LIGHT_BORDER};
  }}
  tbody td {{
    padding: 12px 14px;
    border-bottom: 1px solid {LIGHT_BORDER};
    color: {TEXT_PRIMARY};
  }}
  tbody tr:hover {{ background: rgba(29,79,145,0.04); }}

  /* Pretty footer */
  .app-footer {{
    text-align: center;
    padding: 20px;
    color: {TEXT_TERTIARY};
    font-size: 0.78rem;
    border-top: 1px solid {LIGHT_BORDER};
    margin-top: 32px;
  }}
</style>
"""


def plotly_layout(title: str | None = None) -> dict:
    """Layout padrão para Plotly em harmonia com o tema."""
    return {
        "title": {
            "text": title,
            "font": {"family": "Sora, sans-serif", "size": 14, "color": THEME_BLUE},
            "x": 0.02,
        } if title else None,
        "paper_bgcolor": WHITE,
        "plot_bgcolor": WHITE,
        "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY, "size": 12},
        "margin": {"l": 50, "r": 30, "t": 40 if title else 20, "b": 40},
        "xaxis": {
            "showgrid": True,
            "gridcolor": LIGHT_BORDER,
            "linecolor": LIGHT_BORDER,
            "zerolinecolor": LIGHT_BORDER,
            "tickfont": {"size": 11, "color": TEXT_SECONDARY},
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": LIGHT_BORDER,
            "linecolor": LIGHT_BORDER,
            "zerolinecolor": LIGHT_BORDER,
            "tickfont": {"size": 11, "color": TEXT_SECONDARY},
        },
        "hoverlabel": {
            "bgcolor": THEME_BLUE,
            "bordercolor": THEME_BLUE,
            "font": {"color": "#ffffff", "family": "Inter, sans-serif"},
        },
        "legend": {"font": {"size": 11, "color": TEXT_SECONDARY}},
        "hovermode": "x unified",
    }
