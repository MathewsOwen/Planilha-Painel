"""Planilha Painel — dashboard Streamlit a partir de CSV.

Lê data/planilha.csv (ou planilha.exemplo.csv) e atualiza ao recarregar.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from branding import APP_FILE_PREFIX, APP_FOOTER, APP_NAME, APP_SUBTITLE, APP_TITLE
from src.loader import load_data, get_file_mtime, CID_NAMES
from src.styling import CUSTOM_CSS
from src.metrics import (
    kpis,
    regional_summary,
    recurrence_table,
    cid_breakdown,
    cid_block_breakdown,
    cargo_breakdown,
    monthly_trend,
    age_distribution,
    duration_distribution,
    detect_insights,
    model_cities,
)
from src.chart_theme import PLOTLY_CONFIG
from src.charts import (
    monthly_chart,
    cid_donut,
    cid_top_bar,
    cargo_bar,
    cargo_dias_bar,
    age_bar,
    duration_pie,
    regional_bar,
)


def _resolve_data_file() -> Path:
    base = Path(__file__).parent / "data"
    local = base / "planilha.csv"
    if local.exists():
        return local
    return base / "planilha.exemplo.csv"


DATA_FILE = _resolve_data_file()


# ----------------- CONFIG INICIAL -----------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------- CACHE -----------------
@st.cache_data(show_spinner="Carregando planilha...")
def _load_cached(path: str, mtime: float) -> pd.DataFrame:
    return load_data(path)


def load_dataset() -> pd.DataFrame:
    if not DATA_FILE.exists():
        st.error(
            f"⚠️ Planilha não encontrada em `{DATA_FILE.relative_to(Path(__file__).parent)}`.\n\n"
            "Copie `data/planilha.exemplo.csv` para `data/planilha.csv` ou coloque seu CSV (separador `;`)."
        )
        st.stop()
    mtime = get_file_mtime(DATA_FILE)
    return _load_cached(str(DATA_FILE), mtime)


# ----------------- HEADER -----------------
def render_header(df: pd.DataFrame) -> None:
    from src.loader import MESES_PT

    if df.empty:
        period = "—"
    else:
        d_ini = df["data_inicio"].min()
        d_fim = df["data_inicio"].max()
        ini = f"{MESES_PT[d_ini.month]}/{d_ini.year}"
        fim = f"{MESES_PT[d_fim.month]}/{d_fim.year}"
        period = f"{ini} – {fim}"

    last_update = datetime.fromtimestamp(get_file_mtime(DATA_FILE)).strftime("%d/%m/%Y %H:%M")

    st.markdown(
        f"""
        <div class="app-header">
          <div>
            <h1>{APP_NAME}</h1>
            <p>{APP_SUBTITLE}</p>
            <span class="app-badge">● Atualização automática a partir da planilha</span>
          </div>
          <div style="text-align:right;">
            <div class="app-period">{period}</div>
            <div class="app-period-sub">Última atualização: {last_update}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------- SIDEBAR FILTROS -----------------
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("### Filtros")
        st.caption("Refine a análise — os gráficos respondem em tempo real.")

        if df.empty:
            return df

        min_date = df["data_inicio"].min().date()
        max_date = df["data_inicio"].max().date()
        date_range = st.date_input(
            "Período (data de início)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
        )

        cargos = ["Todos"] + sorted(df["cargo"].dropna().unique().tolist())
        cargo_sel = st.multiselect("Cargo", cargos, default=["Todos"])

        regionais = ["Todas"] + sorted(df["regional"].dropna().unique().tolist())
        regional_sel = st.multiselect("Superintendência", regionais, default=["Todas"])

        blocos = ["Todos"] + sorted(df["cid_block"].dropna().unique().tolist())
        bloco_sel = st.multiselect("Bloco CID", blocos, default=["Todos"])

        faixas = ["Todas", "Até 30", "31–40", "41–50", "51–60", "60+", "Não informado"]
        faixa_sel = st.multiselect("Faixa etária", faixas, default=["Todas"])

        st.markdown("---")
        if st.button("🔄 Recarregar planilha", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.caption(
            "💡 **Dica:** edite o arquivo `data/planilha.csv` na raiz do projeto. "
            "Salve e clique em recarregar (ou aperte `R`)."
        )

        with st.expander("ℹ️ Sobre os dados"):
            st.markdown(
                f"""
                - **Total bruto:** {len(df)} registros
                - **CIDs únicos:** {df['cid_group'].nunique()}
                - **Regionais:** {df['regional'].nunique()}
                - **Coluna gênero:** ignorada por requisito
                """
            )

    # Aplicar filtros
    filtered = df.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            (filtered["data_inicio"].dt.date >= start)
            & (filtered["data_inicio"].dt.date <= end)
        ]

    if cargo_sel and "Todos" not in cargo_sel:
        filtered = filtered[filtered["cargo"].isin(cargo_sel)]
    if regional_sel and "Todas" not in regional_sel:
        filtered = filtered[filtered["regional"].isin(regional_sel)]
    if bloco_sel and "Todos" not in bloco_sel:
        filtered = filtered[filtered["cid_block"].isin(bloco_sel)]
    if faixa_sel and "Todas" not in faixa_sel:
        filtered = filtered[filtered["faixa_etaria"].isin(faixa_sel)]

    return filtered


# ----------------- KPI GRID -----------------
def render_kpis(df: pd.DataFrame) -> None:
    k = kpis(df)
    cols = st.columns(5, gap="medium")

    cards = [
        ("", "Total de Registros", f"{k['total_registros']:,}".replace(",", "."), "afastamentos no período"),
        ("warn", "Total de Dias Perdidos", f"{k['total_dias']:,}".replace(",", "."), "dias acumulados"),
        ("accent", "Média por Evento", f"{k['media_dias']:.1f}".replace(".", ","), "dias por afastamento"),
        ("danger", "Regionais Críticas", f"{k['regionais_criticas']}", "superintendências em alerta"),
        (
            "success",
            "CID Predominante",
            k["cid_predominante"],
            f"{k['cid_predominante_nome']} · {k['cid_predominante_count']} casos",
        ),
    ]

    for col, (klass, label, value, sub) in zip(cols, cards):
        cls_attr = f"kpi-card {klass}" if klass else "kpi-card"
        col.markdown(
            f"""
            <div class="{cls_attr}">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{value}</div>
              <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ----------------- INSIGHTS -----------------
def render_insights(df: pd.DataFrame) -> None:
    insights = detect_insights(df)
    cols_html = ""
    for i in insights:
        cols_html += f"""
        <div>
          <div class="insight-num">{i['num']}</div>
          <div class="insight-label">{i['label']}</div>
        </div>
        """
    st.markdown(
        f"""
        <div class="insight-box" style="display:grid;grid-template-columns:repeat({len(insights)},1fr);gap:24px;">
          {cols_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------- REGIONAIS CRÍTICAS -----------------
def render_critical_regions(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Regiões com maior incidência</div>', unsafe_allow_html=True)

    summary = regional_summary(df)
    if summary.empty:
        st.info("Sem dados regionais para o filtro atual.")
        return

    top = summary.head(5)
    pill_map = {
        "CRÍTICO": ("critico", "pill-critico"),
        "ALTO": ("alto", "pill-alto"),
        "MÉDIO": ("medio", "pill-medio"),
        "BAIXO": ("baixo", "pill-baixo"),
    }
    rows_html = ""
    for idx, row in enumerate(top.itertuples(index=False), start=1):
        cls, pill = pill_map.get(row.risco, ("medio", "pill-medio"))
        media = float(row.media_dias) if pd.notna(row.media_dias) else 0
        rows_html += f"""
        <div class="city-row {cls}">
          <div class="city-rank">{idx}</div>
          <div style="flex:1;">
            <div class="city-name">{row.regional}</div>
            <div class="city-meta">{row.eventos} eventos · {int(row.dias or 0)} dias acumulados · média {media:.1f}d · CID princ. {row.cid_top or '—'}</div>
          </div>
          <div class="city-pill {pill}">{row.risco}</div>
        </div>
        """
    st.markdown(rows_html, unsafe_allow_html=True)


# ----------------- RECORRÊNCIA -----------------
def render_recurrence(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Servidores com maior recorrência</div>', unsafe_allow_html=True)
    rec = recurrence_table(df)
    if rec.empty:
        st.info("Sem dados de recorrência para o filtro atual.")
        return
    top = rec[rec["eventos"] >= 2].head(8).copy()
    if top.empty:
        st.success("✓ Nenhum servidor com 2+ afastamentos identificado no filtro atual.")
        return

    top["servidor"] = (
        top["cargo"].fillna("—")
        + " · "
        + top["regional"].fillna("—")
        + " · "
        + top["lotacao"].fillna("—").str.slice(0, 40)
        + " · "
        + top["idade"].fillna(0).astype(int).astype(str) + " anos"
    )

    display = top[["servidor", "eventos", "dias_totais"]].rename(
        columns={"servidor": "Servidor (proxy)", "eventos": "Afastamentos", "dias_totais": "Dias totais"}
    )
    display["Dias totais"] = display["Dias totais"].fillna(0).astype(int)
    st.dataframe(display, hide_index=True, use_container_width=True, height=min(360, 56 * (len(display) + 1)))
    st.caption(
        "⚠️ Como a planilha não tem ID único, o agrupamento usa cargo + regional + lotação + idade como proxy. "
        "Pode incluir falsos positivos."
    )


# ----------------- CID -----------------
def render_cid_section(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Classificação por CID</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1.1, 1], gap="large")

    with col_a:
        st.markdown('<div class="card-app"><div class="card-title">Top CIDs (códigos a 3 dígitos)</div>', unsafe_allow_html=True)
        top = cid_breakdown(df, top_n=8)
        st.plotly_chart(cid_top_bar(top), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card-app"><div class="card-title">Distribuição por bloco CID</div>', unsafe_allow_html=True)
        blocks = cid_block_breakdown(df)
        st.plotly_chart(cid_donut(blocks), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------- CARGO -----------------
def render_cargo_section(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Afastamentos por cargo</div>', unsafe_allow_html=True)
    cargos = cargo_breakdown(df)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="card-app"><div class="card-title">Volume de afastamentos</div>', unsafe_allow_html=True)
        st.plotly_chart(cargo_bar(cargos), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="card-app"><div class="card-title">Média de dias por evento</div>', unsafe_allow_html=True)
        st.plotly_chart(cargo_dias_bar(cargos), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------- AGE & DURATION -----------------
def render_age_duration(df: pd.DataFrame) -> None:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="card-app"><div class="card-title">Faixa etária</div>', unsafe_allow_html=True)
        st.plotly_chart(age_bar(age_distribution(df)), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="card-app"><div class="card-title">Duração dos afastamentos</div>', unsafe_allow_html=True)
        st.plotly_chart(duration_pie(duration_distribution(df)), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------- REGIONAL PANEL -----------------
def render_regional_panel(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Painel por superintendência</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1.4, 1], gap="large")

    with col_a:
        st.markdown('<div class="card-app"><div class="card-title">Volume por regional (top 10)</div>', unsafe_allow_html=True)
        st.plotly_chart(regional_bar(regional_summary(df), top_n=10), use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card-app"><div class="card-title">Cidades-modelo (baixa incidência)</div>', unsafe_allow_html=True)
        models = model_cities(df, max_cities=6)
        if models.empty:
            st.info("Sem cidades-modelo identificadas com os filtros atuais.")
        else:
            for _, row in models.iterrows():
                media = float(row['media_dias']) if pd.notna(row['media_dias']) else 0
                st.markdown(
                    f"""
                    <div class="city-row baixo">
                      <div style="flex:1;">
                        <div class="city-name">{row['regional']}</div>
                        <div class="city-meta">{int(row['eventos'])} eventos · {int(row['dias'] or 0)} dias · média {media:.1f}d</div>
                      </div>
                      <div class="city-pill pill-baixo">REFERÊNCIA</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------- HEATMAP TABLE -----------------
def render_regional_table(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Tabela detalhada por regional</div>', unsafe_allow_html=True)
    summary = regional_summary(df)
    if summary.empty:
        st.info("Sem dados.")
        return

    summary_display = summary.copy()
    summary_display["dias"] = summary_display["dias"].fillna(0).astype(int)
    summary_display["media_dias"] = summary_display["media_dias"].fillna(0).round(1)
    summary_display = summary_display.rename(
        columns={
            "regional": "Superintendência",
            "eventos": "Eventos",
            "dias": "Dias totais",
            "media_dias": "Média (dias)",
            "cid_top": "CID princ.",
            "risco": "Risco",
        }
    )
    st.dataframe(
        summary_display,
        hide_index=True,
        use_container_width=True,
        height=min(420, 38 * (len(summary_display) + 1)),
        column_config={
            "Risco": st.column_config.TextColumn(width="small"),
            "Eventos": st.column_config.NumberColumn(format="%d"),
            "Dias totais": st.column_config.NumberColumn(format="%d"),
            "Média (dias)": st.column_config.NumberColumn(format="%.1f"),
        },
    )


# ----------------- TEMPORAL -----------------
def render_temporal(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Evolução temporal</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-app"><div class="card-title">Afastamentos por mês (com média móvel de 3 meses)</div>', unsafe_allow_html=True)
    st.plotly_chart(monthly_chart(monthly_trend(df)), use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- PLANO -----------------
def render_action_plan() -> None:
    st.markdown('<div class="section-title">Plano de ação recomendado</div>', unsafe_allow_html=True)
    plans = [
        ("🧠", "Programa de Saúde Mental Corporativo",
         "Estruturar atendimento preventivo com psicólogos e psiquiatras. Foco nos CIDs F41 (ansiedade) e F32 (depressão).",
         "Prevenção"),
        ("🔄", "Protocolo para Recorrência",
         "Identificar servidores com 2+ afastamentos em 12 meses. Avaliação aprofundada e possível adaptação funcional.",
         "Gestão de Casos"),
        ("📋", "Monitoramento Regional",
         "Painel ativo para regionais críticas com alertas quando o volume mensal supera o threshold histórico.",
         "Vigilância"),
        ("🤝", "Apoio ao Retorno ao Trabalho",
         "Reintegração gradual após afastamentos >30 dias: jornada reduzida, adaptação e acompanhamento por 90d.",
         "Reintegração"),
        ("📊", "Benchmarking",
         "Trocar boas práticas entre cidades-modelo e regionais críticas. Mapear diferenciais de clima e gestão.",
         "Boas Práticas"),
        ("🌱", "Cultura de Cuidado",
         "Conscientização e capacitação de gestores para identificação precoce de sinais de adoecimento.",
         "Cultura"),
    ]
    cols = st.columns(3, gap="medium")
    for idx, (icon, title, desc, tag) in enumerate(plans):
        col = cols[idx % 3]
        col.markdown(
            f"""
            <div class="plan-card">
              <div class="plan-icon">{icon}</div>
              <div class="plan-title">{title}</div>
              <div class="plan-desc">{desc}</div>
              <span class="plan-tag">{tag}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ----------------- CONCLUSÃO -----------------
def render_conclusion(df: pd.DataFrame) -> None:
    if df.empty:
        return
    k = kpis(df)
    regional_top = df["regional"].value_counts().head(1)
    regional_label = regional_top.index[0] if len(regional_top) else "—"
    regional_pct = (regional_top.iloc[0] / len(df) * 100) if len(df) else 0

    st.markdown(
        f"""
        <div class="conclusion-card">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:32px;">
            <div>
              <div class="col-title">Padrão Principal</div>
              <p class="col-text">
                Os afastamentos por CID F apresentam duração média de
                <strong>{k['media_dias']:.1f} dias</strong> por evento,
                impacto muito superior ao de outras causas.
                O CID predominante é <strong>{k['cid_predominante']} · {k['cid_predominante_nome']}</strong>.
              </p>
            </div>
            <div>
              <div class="col-title">Alerta</div>
              <p class="col-text">
                A regional <strong>{regional_label}</strong> concentra
                <strong>{regional_pct:.1f}%</strong> dos registros.
                {k['servidores_recorrentes']} casos apresentam recorrência (2+ afastamentos),
                indicando condições crônicas que demandam intervenção.
              </p>
            </div>
            <div>
              <div class="col-title">Oportunidade</div>
              <p class="col-text">
                Com acompanhamento psicológico ativo e protocolos de retorno gradual,
                estima-se possibilidade de <strong>redução de 30–40%</strong> dos dias perdidos
                nas regionais críticas — prevenção sai mais barata que afastamentos longos e recorrentes.
              </p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------- DETAIL TABLE -----------------
def render_detail_table(df: pd.DataFrame) -> None:
    with st.expander("📑 Tabela detalhada de registros (busca e exportação)"):
        if df.empty:
            st.info("Sem registros.")
            return
        display = df[
            ["data_inicio", "data_fim", "dias", "cargo", "regional", "lotacao", "cid_group", "cid_name", "idade", "faixa_etaria"]
        ].copy()
        display = display.rename(
            columns={
                "data_inicio": "Início",
                "data_fim": "Fim",
                "dias": "Dias",
                "cargo": "Cargo",
                "regional": "Regional",
                "lotacao": "Lotação",
                "cid_group": "CID",
                "cid_name": "Descrição CID",
                "idade": "Idade",
                "faixa_etaria": "Faixa",
            }
        )
        display["Início"] = display["Início"].dt.strftime("%d/%m/%Y")
        display["Fim"] = display["Fim"].dt.strftime("%d/%m/%Y")
        st.dataframe(display, hide_index=True, use_container_width=True, height=420)

        csv_bytes = df.to_csv(index=False, sep=";").encode("utf-8-sig")
        st.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=csv_bytes,
            file_name=f"{APP_FILE_PREFIX}_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )


# ----------------- MAIN -----------------
def main():
    df_raw = load_dataset()
    df = render_sidebar(df_raw)

    render_header(df)
    render_kpis(df)
    render_insights(df)

    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        render_critical_regions(df)
    with col_b:
        render_recurrence(df)

    render_temporal(df)
    render_cid_section(df)
    render_cargo_section(df)
    render_age_duration(df)
    render_regional_panel(df)
    render_regional_table(df)
    render_action_plan()
    render_conclusion(df)
    render_detail_table(df)

    st.markdown(
        f"""
        <div class="app-footer">
          {APP_FOOTER} · {len(df)} registros analisados<br>
          Dados editáveis em <code>data/planilha.csv</code> — o dashboard atualiza automaticamente
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
