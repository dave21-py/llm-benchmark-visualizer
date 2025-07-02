import streamlit as st
import pandas as pd
from pathlib import Path
import base64

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="LLM Benchmark Visualizer",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- PATHS & DATA LOADING ---
ASSETS_DIR = Path(__file__).parent / "assets"

# It's better to manage logos in code for this custom table
# We'll create a mapping from creator name to logo filename.
LOGO_MAP = {
    "ZhipuAI": "zhipuai.png",
    "Alibaba": "alibaba.png",
    "DeepSeek": "deepseek.png",
    "01.AI": "01ai.png",
    "Google": "google.png",
    "OpenAI": "openai.png",
    "Meta": "meta.png",
    "Mistral AI": "mistralai.png",
    "Microsoft": "microsoft.png",
    "TinyLlama":   "tinyllama.png",
    "OpenChat":    "openchat.png",
    "Cohere":      "cohere.png"
}

# Load your data
# For this example, I'm creating a sample DataFrame that matches the new structure.
# You should adapt your 'scores.csv' to have these columns.
@st.cache_data
def load_data():
    # ----> REPLACE THIS WITH YOUR DF LOADING (pd.read_csv("scores.csv"))
    data = {
       "model_name": [
           "GLM-4-9B-Chat",
           "Qwen2-72B-Instruct",
           "DeepSeek-V2",
           "Yi-Large",
           "Gemini 1.5 Pro",
           "GPT-4o-mini",
           "Llama-3-70B-Instruct",
           "Mistral-7B-v0.2",
           "Phi-3-Mini-3.8B-Instruct",
           "TinyLlama-1.1B-Chat",
           "OpenChat-3.5",
           "Command R+"
      ],
      
      "creator": [
          "ZhipuAI",
          "Alibaba",
          "DeepSeek",
          "01.AI",
          "Google",
          "OpenAI",
          "Meta",
          "Mistral AI",
          "Microsoft",
          "TinyLlama",
          "OpenChat",
          "Cohere"
      ],
      
      "origin": [
          "China", "China", "China", "China",
          "USA", "USA", "USA",
          "France", "USA",
          "Community", "Community", "Canada"
      ],
      
      "performance_score": [75.1, 78.5, 77.2, 76.8, 72.5, 73.0, 82.1, 79.4, 75.6, 68.0, 74.3, 71.0],
  
      "price_input_usd_per_1m":  [0.0017, 0.0112, 0.0014, 0.0028, 3.50, 0.15, 0.0008, 0.0004, 0.0002, 0.0001, 0.0003, 0.0004],
      "price_output_usd_per_1m": [0.0017, 0.0336, 0.0028, 0.0084, 10.50, 0.60, 0.0024, 0.0012, 0.0006, 0.0003, 0.0009, 0.0010],
      
      "speed_tokens_s":  [205, 95, 150, 110, 146, 163, 160, 210, 300, 320, 280, 250],
      "context_window_k": [128, 128, 128, 200, 1000, 128, 128, 32, 128, 128, 128, 128],

      "type": [
          "Open Source", "Open Source", "Open Source", "Open Source",
          "Proprietary", "Proprietary",
          "Open Source", "Open Source", "Open Source",
          "Open Source", "Open Source", "Open Source"
      ],
       
      "updated_at": pd.to_datetime([
          "2025-06-28", "2025-06-20", "2025-06-18", "2025-06-15",
          "2025-06-13", "2025-06-13", "2025-06-10", "2025-06-08",
          "2025-06-05", "2025-05-30", "2025-05-28", "2025-05-25"
      
      ])      

    }
    df = pd.DataFrame(data)
    # <---- END OF REPLACEMENT SECTION

    df["logo"] = df["creator"].map(LOGO_MAP)
    # Create a blended price for sorting. You can adjust the weights.
    df['blended_price'] = (df['price_input_usd_per_1m'] * 0.75) + (df['price_output_usd_per_1m'] * 0.25)
    return df

df = load_data()


# --- CUSTOM CSS ---
def load_css():
    st.markdown("""
    <style>
        :root {
            --main-bg: var(--background-color);
            --text-main: var(--text-color);
            --card-bg: var(--secondary-background-color);
            --accent: var(--primary-color);
            --muted: #A0A0A0;
        }

        body {
            background-color: var(--main-bg);
            color: var(--text-main);
        }

        .main .block-container {
            padding: 2rem 3rem;
        }

        #MainMenu, .stDeployButton, footer {
            display: none;
        }

        .stButton>button {
            background-color: var(--card-bg);
            border: 1px solid var(--muted);
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            color: var(--text-main);
        }

        .stButton>button:hover {
            background-color: var(--accent);
            border-color: var(--text-main);
            color: #fff;
        }

        .stSelectbox div[data-baseweb="select"] > div {
            background-color: var(--card-bg);
            border-radius: 0.5rem;
        }

        /* Title & Subtitle */
        h1 {
            font-size: 2.8rem;
            font-weight: 700;
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: var(--muted);
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        /* KPI Cards */
        .kpi-card {
            border-radius: 12px;
            padding: 18px 16px;
            background-color: var(--card-bg);
            border: 1px solid var(--muted);
            text-align: center;
        }

        .kpi-title {
            font-size: 0.9rem;
            color: var(--muted);
            margin-bottom: 8px;
        }

        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-main);
        }

        /* Table Styling */
        .table-header, .table-row {
            font-size: 0.9rem;
            color: var(--text-main);
        }

        .table-row {
            border-bottom: 1px solid var(--muted);
        }

        .table-row:hover {
            background-color: rgba(100, 100, 100, 0.05);
        }

        .model-name {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text-main);
        }

        .creator-name {
            font-size: 0.9rem;
            color: var(--muted);
        }

        .metric-value {
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-main);
            text-align: right;
        }

        .metric-unit {
            font-size: 0.8rem;
            color: var(--muted);
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)


load_css()

# --- HEADER SECTION ---
st.title("LLM Benchmark Visualizer")
st.markdown("<p class='subtitle'>Live, side-by-side metrics for open-source and proprietary LLMs – "
    "performance × price × speed.</p>", unsafe_allow_html=True)

# --- KPI CARDS ---
c1, c2, c3 = st.columns(3)
kpi_cfg = [
    (c1, "🧠 Models Tracked", f"{df['model_name'].nunique():,}"),
    (c2, "🏆 Top Performance", f"{df['performance_score'].max():.1f}"),
    (c3, "📅 Last Update", f"{df['updated_at'].max().date()}"),
]
for col, title, val in kpi_cfg:
    with col:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <p class="kpi-value">{val}</p>
            </div>""", unsafe_allow_html=True)

st.write("---")

# --- FILTERS & SORTING ---
st.subheader("Explore the Leaderboard")
filter_cols = st.columns([1, 1, 2])
with filter_cols[0]:
    origin_filter = st.selectbox('**Origin**', ['All'] + list(df['origin'].unique()))
with filter_cols[1]:
    type_filter = st.selectbox('**Model Type**', ['All', 'Open Source', 'Proprietary'])

sort_by = st.selectbox(
    '**Sort By**',
    options=['performance_score', 'blended_price', 'speed_tokens_s', 'context_window_k'],
    format_func=lambda x: {
        'performance_score': 'Performance (High to Low)', 'blended_price': 'Price (Low to High)',
        'speed_tokens_s': 'Speed (High to Low)', 'context_window_k': 'Context (High to Low)'
    }[x]
)

# --- FILTERING & SORTING LOGIC ---
filtered_df = df.copy()
if origin_filter != 'All':
    filtered_df = filtered_df[filtered_df['origin'] == origin_filter]
if type_filter != 'All':
    filtered_df = filtered_df[filtered_df['type'] == type_filter]

ascending = True if sort_by == 'blended_price' else False
sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

# --- CUSTOM LEADERBOARD TABLE ---
st.markdown("<div class='table-container'>", unsafe_allow_html=True)

# Table Header
header_cols = st.columns([3, 2, 2, 2, 2])
header_cols[0].markdown("<div class='table-header model-col'>MODEL</div>", unsafe_allow_html=True)
header_cols[1].markdown("<div class='table-header'>PERFORMANCE</div>", unsafe_allow_html=True)
header_cols[2].markdown("<div class='table-header'>PRICE (blended)</div>", unsafe_allow_html=True)
header_cols[3].markdown("<div class='table-header'>SPEED</div>", unsafe_allow_html=True)
header_cols[4].markdown("<div class='table-header'>CONTEXT</div>", unsafe_allow_html=True)

# Table Rows
for _, row in sorted_df.iterrows():
    row_cols = st.columns([3, 2, 2, 2, 2])
    
    # Column 1: Model, Creator, Logo
    logo_path = ASSETS_DIR / row.get('logo', '')
    if logo_path.is_file():
        img_bytes = logo_path.read_bytes()
        encoded = base64.b64encode(img_bytes).decode()
        logo_html = f"<img src='data:image/png;base64,{encoded}' class='logo-img'>"
    else:
        logo_html = "<div class='logo-img' style='background-color:#333;'></div>" # Placeholder

    row_cols[0].markdown(f"""
        <div class='table-row model-cell'>
            {logo_html}
            <div>
                <div class='model-name'>{row['model_name']}</div>
                <div class='creator-name'>{row['creator']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Metric columns
    #Performance
    row_cols[1].markdown(
        f"<div class='table-row'>"
        f"<div class='metric-value'>{row['performance_score']:.1f}</div>"
        f"<div class='metric-unit'>C-Eval Score</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    # Blended price
    row_cols[2].markdown(
        f"<div class='table-row'>"
        f"<div class='metric-value'>${row['blended_price']:.4f}</div>"
        f"<div class='metric-unit'>USD/1M Tokens</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    # Speed
    row_cols[3].markdown(
        f"<div class='table-row'>"
        f"<div class='metric-value'>{int(row['speed_tokens_s'])}</div>"
        f"<div class='metric-unit'>Tokens/s</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    # Context window
    row_cols[4].markdown(
        f"<div class='table-row'>"
        f"<div class='metric-value'>{int(row['context_window_k'])}k</div>"
        f"<div class='metric-unit'>Tokens</div>"
        f"</div>",
        unsafe_allow_html=True
    )

# --- VISUALIZATION ---
import matplotlib.pyplot as plt
import seaborn as sns


st.subheader("📊 Metric Visualiser")

metric = st.radio(
    "Select metric to visualize:",
    ["performance_score", "blended_price", "speed_tokens_s"],
    format_func=lambda x: {
        "performance_score": "C-Eval Score",
        "blended_price": "Price (USD/1M tokens)",
        "speed_tokens_s": "Tokens per second"
    }[x],
    horizontal=True
)

df_chart = sorted_df.copy()

sns.set(style="darkgrid")

ascending = True if metric == "blended_price" else False
top_df = df_chart.sort_values(by=metric, ascending=ascending).head(12)

palette = sns.color_palette("Blues_r", len(top_df))


fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=top_df,
    x="model_name",
    y=metric,
    palette=palette,
    ax=ax
)

ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.tick_params(axis='x', labelsize=10)

for i, value in enumerate(top_df[metric]):
    ax.text(i, value + 0.5, f"{value:.2f}", color='black', va='center', fontsize=9)

label = {
    "performance_score": "C-Eval Score",
    "blended_price": "Price (USD/1M tokens)",
    "speed_tokens_s": "Tokens per second"
}[metric]

ax.set_title(f"{label} – Top 12 Models", fontsize=16, fontweight='bold')
ax.set_xlabel(label, fontsize=12)
ax.set_ylabel("")

st.pyplot(fig)



# --- FOOTER & METHODOLOGY ---
st.write("---")
with st.expander("Methodology & About this Project"):
    st.markdown("""
 <div style="line-height: 1.6;">
     <b>🧐 About This Project</b>
     <p>
        This is an open-source project dedicated to benchmarking Large Language Models, with a special focus on models from Asia and beyond.
     </p>
<ul>
 <li><b>Performance Score:</b> We use the <b>C-Eval</b> score as a 
 primary metric, a comprehensive Chinese evaluation suite for foundation models.</li>
<li><b>Price:</b> A blended price is calculated (75% input, 25% 
output) from public data, in USD per 1 million tokens.</li>
 <li><b>Speed:</b> Measured in tokens per second on standardized 
hardware.</li>
</ul>
<p>
This project is for demonstration and portfolio purposes only. The data is a representative sample.
</p>
 <br>

 <b>🔗 Contribute & Follow</b><br>
<a href="https://github.com/dave21-py" target="_blank">GitHub</a> | 
<a href="https://www.linkedin.com/in/david-geddam/"
target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
