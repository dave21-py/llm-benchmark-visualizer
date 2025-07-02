# -*- coding: utf-8 -*-
# APAC LLM Benchmark Dashboard · v2
# Inspired by artificialanalysis.ai & HF LLM-Performance-Leaderboard

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# --------------------------------------------------  Page config
st.set_page_config(
    page_title="APAC LLM Benchmark Dashboard",
    page_icon="📊",
    layout="wide",
)

# --------------------------------------------------  LOAD DATA
df = pd.read_csv("scores.csv", parse_dates=["updated_at"])
df["api_provider"] = "OpenAI"


FLAG = {"CN": "🇨🇳", "JP": "🇯🇵", "IN": "🇮🇳"}
PROVIDER_LOGO = {
    "OpenAI":   "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/openai.svg",
    "Google":   "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/google.svg",
    "Microsoft Azure": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/microsoftazure.svg",
    "deepseek": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/deepnote.svg",     # placeholder
}

df["Country"] = df["country"].map(FLAG).fillna(df["country"])
df["Provider"] = df["api_provider"].map(  # requires api_provider col
    lambda p: f'<img src="{PROVIDER_LOGO.get(p,"")}" width="18"/> {p}'
    if p in PROVIDER_LOGO else p,
    na_action="ignore"
)
df["Updated"] = df["updated_at"].dt.date
df["Params (B)"] = df["param_B"]
df["Score"] = df["score"]

# --------------------------------------------------  SIDEBAR
with st.sidebar:
    st.header("🔍 Filter options")
    bench_choice   = st.selectbox("Benchmark", ["All"] + sorted(df["benchmark_name"].unique()))
    country_choice = st.multiselect(
        "Country", options=list(FLAG.values()), default=list(FLAG.values())
    )
    st.markdown("---")
    st.caption("💡 Tip: ⌘/Ctrl + click to select multiple.")

# --------------------------------------------------  FILTER
filt = df.copy()
if bench_choice != "All":
    filt = filt[filt["benchmark_name"] == bench_choice]
if country_choice:
    filt = filt[filt["Country"].isin(country_choice)]

# --------------------------------------------------  KPI row
kpi_cfg = [
    ("🧠 Models",          len(filt)),
    ("🏆 Top score",       filt["Score"].max() if not filt.empty else float("nan")),
    ("🗓️ Last update",     filt["Updated"].max() if not filt.empty else pd.NaT),
]
kpi_cols = st.columns(3)
for (title, val), col in zip(kpi_cfg, kpi_cols):
    col.markdown(
        f"""
        <div style="background:#111218;padding:14px 18px;border-radius:12px;
                    text-align:center;box-shadow:0 0 9px rgba(0,0,0,.25);">
            <div style="font-size:.80rem;color:#888;">{title}</div>
            <div style="font-weight:800;font-size:1.5rem;margin-top:2px;">{val}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# --------------------------------------------------  Leaderboard (AG-Grid)
st.subheader("Leaderboard")
if filt.empty:
    st.warning("No models found for this selection. Try a different filter.")
else:
    # Style: blue gradient + gold threshold + row-hover
    def style_score(val):
        base = "background-color:"
        if val > 1000:            # dynamic threshold
            return f"{base}gold;font-weight:bold;color:black"
        return ""

    gb = GridOptionsBuilder.from_dataframe(
        filt[
            ["Provider", "model_name", "benchmark_name", "Score",
             "Params (B)", "Country", "Updated"]
        ]
    )
    gb.configure_default_column(resizable=True, sortable=True, filter=True)
    gb.configure_column("Provider", header_name="API Provider", sortable=True)
    gb.configure_column("model_name", header_name="Model", minWidth=190)
    gb.configure_column("benchmark_name", header_name="Benchmark", minWidth=160)
    gb.configure_column("Score", type=["numericColumn","numberColumnFilter"])
    gb.configure_column("Params (B)", type=["numericColumn"])
    gb.configure_column("Country", maxWidth=90)
    gb.configure_column("Updated", maxWidth=110)
    grid_opts = gb.build()


    AgGrid(
        filt,
        gridOptions=grid_opts,
        theme="balham-dark",
        height=min(480, 34 + 26 * len(filt)),
        fit_columns_on_grid_load=True,
    )

st.divider()

# --------------------------------------------------  Top-N bar chart (Altair)
st.subheader("Top 15 models by score")
if not filt.empty:
    top15 = filt.nlargest(15, "Score").sort_values("Score")
    import altair as alt
    bar = alt.Chart(top15).mark_bar().encode(
        x=alt.X("Score:Q", title=""),
        y=alt.Y("model_name:N", sort=None, title=""),
        color=alt.condition(
            alt.datum.Score > 1000, alt.value("gold"), alt.value("#1e88e5")
        ),
        tooltip=["model_name", "benchmark_name", "Score", "Params (B)"]
    ).properties(height=350)
    st.altair_chart(bar, use_container_width=True)

# --------------------------------------------------  Download
csv = filt.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download filtered CSV", csv, "filtered_apac_llm_scores.csv")

