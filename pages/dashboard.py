import streamlit as st
from supabase import create_client
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
from urllib.parse import quote
import pandas as pd
import altair as alt

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title='LEADBOOST DASHBOARD',
    page_icon='#',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# ======================================================
# THEME STATE
# ======================================================
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# ======================================================
# THEME COLORS
# ======================================================
if st.session_state.theme == 'light':
    BG = '#F2EDE2'
    PANEL = '#FAF5E9'
    BORDER = '#D8D0BC'
    TEXT = '#1C1C1A'
    TEXT_DIM = '#8A8473'
    ACCENT = '#1C1C1A'
    ACCENT_WARM = '#C4633F'
    CHART_FILL = '#E8C9A8'
    CHART_LINE = '#C4633F'
    HOT_BG = '#EDD5CC'
    WARM_BG = '#E8DCC0'
    COLD_BG = '#D6D9CD'
    WARM_ACCENT = '#B8924A'
else:
    BG = '#18150F'
    PANEL = '#221E16'
    BORDER = '#3A342A'
    TEXT = '#EDE6D4'
    TEXT_DIM = '#8A8473'
    ACCENT = '#EDE6D4'
    ACCENT_WARM = '#D47A4D'
    CHART_FILL = '#4A3826'
    CHART_LINE = '#D47A4D'
    HOT_BG = '#3A2820'
    WARM_BG = '#332B1E'
    COLD_BG = '#252420'
    WARM_ACCENT = '#C4A35A'

# ======================================================
# CSS
# ======================================================
css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300;1,9..144,400&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp, .main {
    font-family: Inter, sans-serif;
    background-color: BG_COLOR !important;
    color: TEXT_COLOR !important;
}
.stApp { background-color: BG_COLOR !important; }
.block-container {
    padding-top: 0.55rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1280px !important;
}

/* Hide Streamlit chrome */
header { visibility: hidden; height: 0 !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
.vega-embed details { display: none !important; }
.vega-embed summary { display: none !important; }
.vega-embed .vega-actions { display: none !important; }

/* Slim scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: BG_COLOR; }
::-webkit-scrollbar-thumb { background: BORDER_COLOR; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: TEXT_DIM_COLOR; }

/* ---- ANIMATIONS ---- */
@keyframes lb-hot-pulse {
    0%   { transform:scale(1);   opacity:.65; }
    70%  { transform:scale(2.4); opacity:0; }
    100% { transform:scale(2.4); opacity:0; }
}
@keyframes lb-fade-up {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes lb-fade-in {
    from { opacity:0; }
    to   { opacity:1; }
}
@keyframes lb-grow-x {
    from { transform: scaleX(0); opacity: 0.4; }
    to   { transform: scaleX(1); opacity: 1; }
}

/* Selection color */
::selection { background: ACCENT_WARM_COLOR; color: BG_COLOR; }

/* ---- TOPBAR ---- */
.lb-topbar-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    padding-top: 14px;
    padding-bottom: 2px;
}

/* ---- HERO ---- */
.lb-hero {
    border: 1px solid BORDER_COLOR;
    background: PANEL_COLOR;
    border-radius: 16px;
    padding: 34px 38px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 28px;
}
.lb-hero-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    letter-spacing: 0.24em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.lb-hero-title {
    font-family: Fraunces, serif;
    font-size: 4rem;
    color: TEXT_COLOR;
    line-height: 0.95;
    font-style: italic;
    font-weight: 300;
    letter-spacing: -0.035em;
}
.lb-hero-accent { color: ACCENT_WARM_COLOR; }

/* ---- BRIEFING PROSE ---- */
.lb-briefing {
    font-family: Fraunces, serif;
    font-size: 1.15rem;
    font-weight: 300;
    color: TEXT_COLOR;
    margin-top: 18px;
    line-height: 1.55;
    max-width: 680px;
    letter-spacing: -0.005em;
    animation: lb-fade-in 0.5s ease both 0.15s;
}
.b-num {
    font-style: italic;
    color: TEXT_COLOR;
    font-weight: 400;
}
.b-num-accent {
    font-style: italic;
    color: ACCENT_WARM_COLOR;
    font-weight: 400;
}
.b-place {
    font-style: italic;
    color: ACCENT_WARM_COLOR;
    font-weight: 400;
}
.lb-hero-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
}
.lb-hero-ring-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
}
.lb-hero-ring-stats {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-align: right;
}
.lb-hero-ring-stat {
    font-family: JetBrains Mono, monospace;
    font-size: 0.54rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: TEXT_DIM_COLOR;
}
.lb-hero-ring-stat.hot { color: ACCENT_WARM_COLOR; }
.lb-hero-date {
    font-family: JetBrains Mono, monospace;
    font-size: 0.58rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.12em;
    text-align: right;
    line-height: 1.7;
}

/* ---- SECTION LABEL ---- */
.section-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    padding-top: 28px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}
.section-label-left {
    display: flex;
    align-items: baseline;
    gap: 10px;
}
.section-num {
    font-family: Fraunces, serif;
    font-style: italic;
    font-weight: 300;
    font-size: 1.15rem;
    color: TEXT_COLOR;
    letter-spacing: -0.02em;
    line-height: 1;
}
.section-sep {
    color: BORDER_COLOR;
    font-weight: 300;
    font-size: 0.9rem;
    font-family: Fraunces, serif;
    font-style: italic;
}
.section-count {
    font-family: Fraunces, serif;
    font-size: 0.95rem;
    font-style: italic;
    font-weight: 300;
    color: TEXT_DIM_COLOR;
}

/* ---- STAT CARDS ---- */
.stat-card {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 20px 22px;
    height: 168px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: border-color 0.2s, transform 0.2s;
}
.stat-card:hover {
    border-color: TEXT_DIM_COLOR;
    transform: translateY(-1px);
}
/* legacy classes kept for backwards-compat — no special border now */
.stat-card-default, .stat-card-hot, .stat-card-warm, .stat-card-cold { }
.stat-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.54rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.stat-value {
    font-family: Fraunces, serif;
    font-size: 3rem;
    color: TEXT_COLOR;
    line-height: 1;
    font-style: italic;
    font-weight: 300;
    letter-spacing: -0.035em;
    font-feature-settings: "tnum";
    font-variant-numeric: tabular-nums;
}
.stat-value-accent {
    font-family: Fraunces, serif;
    font-size: 3rem;
    color: ACCENT_WARM_COLOR;
    line-height: 1;
    font-style: italic;
    font-weight: 300;
    letter-spacing: -0.035em;
    font-feature-settings: "tnum";
    font-variant-numeric: tabular-nums;
}
.stat-spark {
    margin: 4px 0 -2px 0;
    height: 24px;
    display: flex;
    align-items: flex-end;
}
.stat-sub {
    font-family: JetBrains Mono, monospace;
    font-size: 0.5rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

/* ---- ASYMMETRIC KPI HERO ---- */
.big-stat-card {
    position: relative;
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 14px;
    padding: 28px 32px 22px 32px;
    height: 100%;
    min-height: 280px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
    animation: lb-fade-up 0.4s ease both;
}
.big-stat-card:hover { border-color: TEXT_DIM_COLOR; }
.big-stat-bg {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 60%;
    opacity: 0.5;
    pointer-events: none;
}
.big-stat-content { position: relative; z-index: 2; }
.big-stat-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.big-stat-num {
    font-family: Fraunces, serif;
    font-size: 6.5rem;
    color: TEXT_COLOR;
    line-height: 0.92;
    font-style: italic;
    font-weight: 300;
    letter-spacing: -0.04em;
    font-feature-settings: "tnum";
    font-variant-numeric: tabular-nums;
    margin-bottom: 8px;
}
.big-stat-delta {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    letter-spacing: 0.18em;
    color: ACCENT_WARM_COLOR;
    text-transform: uppercase;
}
.big-stat-delta-dim {
    color: TEXT_DIM_COLOR;
}

.mini-stat-stack {
    display: flex;
    flex-direction: column;
    gap: 10px;
    height: 100%;
}
.mini-stat {
    flex: 1;
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    transition: border-color 0.2s, transform 0.2s;
    animation: lb-fade-up 0.4s ease both;
}
.mini-stat:hover { border-color: TEXT_DIM_COLOR; transform: translateY(-1px); }
.mini-stat-left { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.mini-stat-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.52rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.mini-stat-value {
    font-family: Fraunces, serif;
    font-size: 2.2rem;
    color: TEXT_COLOR;
    line-height: 0.95;
    font-style: italic;
    font-weight: 300;
    letter-spacing: -0.03em;
    font-feature-settings: "tnum";
    font-variant-numeric: tabular-nums;
}
.mini-stat-value-accent { color: ACCENT_WARM_COLOR; }
.mini-stat-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    min-width: 90px;
    flex-shrink: 0;
}
.mini-stat-pct {
    font-family: JetBrains Mono, monospace;
    font-size: 0.5rem;
    letter-spacing: 0.14em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.mini-stat-spark {
    width: 100%;
    max-width: 110px;
}

/* ---- CALENDAR HEATMAP ---- */
.heatmap-wrap {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 24px 28px;
    animation: lb-fade-up 0.4s ease both;
}
.heatmap-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 22px;
    padding-bottom: 16px;
    border-bottom: 1px solid BORDER_COLOR;
    gap: 24px;
}
.heatmap-title-block { flex: 1; min-width: 0; }
.heatmap-meta-block {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    flex-shrink: 0;
}
.heatmap-title {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.heatmap-subtitle {
    font-family: Fraunces, serif;
    font-size: 0.95rem;
    color: TEXT_COLOR;
    font-style: italic;
    font-weight: 300;
    line-height: 1.4;
    max-width: 480px;
    letter-spacing: -0.005em;
}
.heatmap-meta {
    font-family: Fraunces, serif;
    font-size: 1.1rem;
    color: TEXT_COLOR;
    font-style: italic;
    font-weight: 300;
}
.heatmap-busiest {
    font-family: JetBrains Mono, monospace;
    font-size: 0.46rem;
    letter-spacing: 0.18em;
    color: ACCENT_WARM_COLOR;
    text-transform: uppercase;
}
.heatmap-svg-wrap {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    padding: 6px 0;
}
.heatmap-legend {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 14px;
    font-family: JetBrains Mono, monospace;
    font-size: 0.46rem;
    letter-spacing: 0.16em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.heatmap-legend-cells { display: inline-flex; gap: 3px; }
.heatmap-legend-cell {
    width: 11px;
    height: 11px;
    border-radius: 2px;
    background: ACCENT_WARM_COLOR;
}

/* ---- PULL-QUOTE CALLOUTS ---- */
.pull-quote {
    display: flex;
    align-items: stretch;
    gap: 24px;
    padding: 32px 8px 32px 4px;
    margin: 14px 0 6px 0;
    animation: lb-fade-up 0.5s ease both;
}
.pull-quote-rule {
    width: 3px;
    background: ACCENT_WARM_COLOR;
    border-radius: 2px;
    flex-shrink: 0;
}
.pull-quote-content { flex: 1; }
.pull-quote-text {
    font-family: Fraunces, serif;
    font-style: italic;
    font-weight: 300;
    font-size: 2.2rem;
    color: TEXT_COLOR;
    line-height: 1.2;
    letter-spacing: -0.025em;
    margin-bottom: 10px;
    max-width: 880px;
}
.pull-quote-text-accent { color: ACCENT_WARM_COLOR; font-weight: 400; }
.pull-quote-attr {
    font-family: JetBrains Mono, monospace;
    font-size: 0.5rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}

/* ---- STAGGERED ANIMATION ---- */
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(1) .stat-card,
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(1) .mini-stat,
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(1) .resp-card { animation-delay: 0ms; }
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(2) .stat-card,
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(2) .mini-stat,
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(2) .resp-card { animation-delay: 70ms; }
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(3) .stat-card,
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(3) .mini-stat,
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(3) .resp-card { animation-delay: 140ms; }
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-child(4) .stat-card { animation-delay: 210ms; }

/* ---- FUNNEL STRIP ---- */
.funnel-strip {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}
.funnel-step { flex: 1; text-align: center; }
.funnel-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.5rem;
    letter-spacing: 0.2em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.funnel-num {
    font-family: Fraunces, serif;
    font-size: 1.7rem;
    font-style: italic;
    font-weight: 300;
    color: TEXT_COLOR;
    line-height: 1;
    font-feature-settings: "tnum";
}
.funnel-pct {
    font-family: JetBrains Mono, monospace;
    font-size: 0.48rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.1em;
    margin-top: 3px;
}
.funnel-arrow {
    font-size: 0.9rem;
    color: BORDER_COLOR;
    padding: 0 8px;
    flex-shrink: 0;
    padding-bottom: 14px;
}

/* ---- CHART PANELS ---- */
.chart-panel {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 14px 18px 6px 18px;
    margin-bottom: 8px;
}
.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid BORDER_COLOR;
}
.chart-title {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    letter-spacing: 0.22em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.chart-big-num {
    font-family: Fraunces, serif;
    font-size: 1rem;
    color: TEXT_COLOR;
    font-style: italic;
    font-weight: 300;
}

/* ---- ZONE LEADERBOARD ---- */
.zone-board {
    display: flex;
    flex-direction: column;
    gap: 9px;
    padding: 4px 0 6px 0;
}
.zone-row {
    display: flex;
    align-items: center;
    gap: 10px;
}
.zone-name {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    letter-spacing: 0.08em;
    color: TEXT_COLOR;
    min-width: 110px;
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.zone-bar-wrap {
    flex: 1;
    height: 4px;
    background: BORDER_COLOR;
    border-radius: 10px;
    overflow: hidden;
}
.zone-bar {
    height: 100%;
    background: CHART_LINE_COLOR;
    border-radius: 10px;
}
.zone-count {
    font-family: JetBrains Mono, monospace;
    font-size: 0.56rem;
    color: TEXT_DIM_COLOR;
    min-width: 18px;
    text-align: right;
}

/* ---- RESPONSE TIME CARD ---- */
.resp-card {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 15px 18px;
    height: 124px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border-top: 3px solid BORDER_COLOR;
}

/* ---- BADGES ---- */
.badge {
    font-family: JetBrains Mono, monospace;
    font-size: 0.5rem;
    letter-spacing: 0.18em;
    padding: 3px 8px;
    border-radius: 20px;
    border: 1px solid BORDER_COLOR;
    text-transform: uppercase;
    font-weight: 500;
    color: TEXT_COLOR;
    display: inline-block;
}
.score-hot { background: HOT_BG_COLOR; border-color: ACCENT_WARM_COLOR; }
.score-warm { background: WARM_BG_COLOR; }
.score-cold { background: COLD_BG_COLOR; }

/* ---- LEAD CARDS ---- */
.lead-card {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 22px 26px;
    margin-bottom: 8px;
    animation: lb-fade-up 0.3s ease both;
    transition: border-color 0.2s, transform 0.2s;
}
.lead-card:hover {
    border-color: TEXT_DIM_COLOR;
    transform: translateY(-1px);
}
.lead-card-hot { border-color: ACCENT_WARM_COLOR55; }
.lead-card-hot:hover { border-color: ACCENT_WARM_COLOR; }
.lead-card-warm { border-color: BORDER_COLOR; }
.lead-card-cold { border-color: BORDER_COLOR; }
.lead-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid BORDER_COLOR;
}
.lead-name {
    font-family: Fraunces, serif;
    font-size: 1.55rem;
    font-style: italic;
    color: TEXT_COLOR;
    font-weight: 300;
    letter-spacing: -0.02em;
}
.lead-badges { display: flex; gap: 5px; align-items: center; }
.lead-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px 22px;
    font-family: JetBrains Mono, monospace;
    font-size: 0.7rem;
    color: TEXT_COLOR;
    margin-bottom: 10px;
}
.field-label {
    color: TEXT_DIM_COLOR;
    font-size: 0.5rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    display: block;
    margin-bottom: 2px;
}
.lead-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 8px;
    padding-top: 9px;
    border-top: 1px solid BORDER_COLOR;
}
.lead-ts {
    font-family: JetBrains Mono, monospace;
    font-size: 0.5rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.wa-btn {
    display: inline-block;
    background: ACCENT_COLOR;
    color: BG_COLOR;
    padding: 6px 14px;
    border-radius: 8px;
    text-decoration: none;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.56rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    transition: opacity 0.15s;
}
.wa-btn:hover { opacity: 0.8; }
.resp-time {
    font-family: JetBrains Mono, monospace;
    font-size: 0.54rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.1em;
}

/* ---- INPUTS ---- */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: PANEL_COLOR !important;
    color: TEXT_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 8px !important;
    font-family: Inter, sans-serif !important;
    font-size: 0.86rem !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
}
.stTextInput > div > div > input:hover,
.stTextArea > div > div > textarea:hover {
    border-color: TEXT_DIM_COLOR !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: ACCENT_WARM_COLOR !important;
    box-shadow: 0 0 0 2px ACCENT_WARM_COLOR33 !important;
    outline: none !important;
}
.stSelectbox > div > div {
    background: PANEL_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 8px !important;
    color: TEXT_COLOR !important;
}
.stTextInput label, .stSelectbox label, .stTextArea label {
    color: TEXT_DIM_COLOR !important;
    font-family: JetBrains Mono, monospace !important;
    font-size: 0.52rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
}

/* ---- BUTTONS ---- */
/* Ghost / secondary buttons (default for all st.button calls) */
div.stButton > button {
    background: transparent;
    color: TEXT_DIM_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 8px;
    padding: 7px 16px;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    transition: all 0.15s;
    white-space: nowrap;
}
div.stButton > button:hover:not(:disabled) {
    border-color: TEXT_COLOR;
    color: TEXT_COLOR;
}
/* Primary solid button (use type='primary' in Python) */
div.stButton > button[kind="primary"] {
    background: ACCENT_COLOR !important;
    color: BG_COLOR !important;
    border: none !important;
    opacity: 1;
}
div.stButton > button[kind="primary"]:hover {
    opacity: 0.85 !important;
}
/* Active status button (disabled=True) — dark accent, restrained */
div.stButton > button:disabled {
    opacity: 1 !important;
    background: ACCENT_COLOR !important;
    color: BG_COLOR !important;
    border: none !important;
    cursor: default !important;
}
/* Download (export) button — ghost */
div.stDownloadButton > button {
    background: transparent;
    color: TEXT_DIM_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 8px;
    padding: 7px 16px;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    white-space: nowrap;
    transition: all 0.15s;
}
div.stDownloadButton > button:hover {
    border-color: TEXT_COLOR;
    color: TEXT_COLOR;
}
/* Theme toggle pill — first stHorizontalBlock, last column */
[data-testid="stHorizontalBlock"]:first-child [data-testid="stColumn"]:last-child div.stButton > button {
    border-radius: 20px !important;
    font-size: 0.5rem !important;
    padding: 3px 10px !important;
    height: auto !important;
    min-height: unset !important;
    line-height: 1.4 !important;
    width: auto !important;
    min-width: unset !important;
    letter-spacing: 0.14em !important;
    box-shadow: none !important;
}

/* ---- EMPTY STATE ---- */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    font-family: Fraunces, serif;
    font-style: italic;
    font-size: 1.2rem;
    font-weight: 300;
    color: TEXT_DIM_COLOR;
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
}

/* ---- NOTES AREA ---- */
.stTextArea { margin-top: 4px !important; }
.stTextArea > div > div > textarea { font-size: 0.8rem !important; }

/* Reduce Streamlit column gap */
[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }

/* ---- COLLAPSIBLE SECTION CARDS (st.expander) ---- */
[data-testid="stExpander"],
div[data-testid="stExpander"] {
    background: PANEL_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    transition: border-color 0.2s !important;
    overflow: hidden !important;
}
[data-testid="stExpander"]:hover,
div[data-testid="stExpander"]:hover {
    border-color: TEXT_DIM_COLOR !important;
}
[data-testid="stExpander"] details {
    background: transparent !important;
    border: none !important;
}
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] summary {
    font-family: JetBrains Mono, monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.22em !important;
    color: TEXT_COLOR !important;
    text-transform: uppercase !important;
    padding: 20px 24px !important;
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    list-style: none !important;
    transition: color 0.2s, background 0.15s !important;
}
[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] summary:hover {
    color: ACCENT_WARM_COLOR !important;
    background: rgba(196, 99, 63, 0.04) !important;
}
[data-testid="stExpander"] details > summary p,
[data-testid="stExpander"] summary p {
    font-family: JetBrains Mono, monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    margin: 0 !important;
}
[data-testid="stExpander"] details[open] > summary {
    border-bottom: 1px solid BORDER_COLOR !important;
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
}
[data-testid="stExpander"] svg {
    fill: TEXT_DIM_COLOR !important;
    color: TEXT_DIM_COLOR !important;
    transition: transform 0.2s !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] details[open] > div {
    padding: 18px 24px 22px 24px !important;
    background: transparent !important;
    animation: lb-fade-in 0.25s ease both !important;
}
/* Reset inner section labels — they're now redundant inside expanders */
[data-testid="stExpander"] .section-label {
    padding-top: 0 !important;
    margin-bottom: 12px !important;
}

/* ---- FOLLOW-UP SCROLLABLE LIST ---- */
.follow-up-list {
    max-height: 312px;
    overflow-y: auto;
    padding-right: 6px;
    margin: 0 -2px;
}
.follow-up-list::-webkit-scrollbar { width: 3px; }
.follow-up-list::-webkit-scrollbar-track { background: transparent; }
.follow-up-list::-webkit-scrollbar-thumb { background: BORDER_COLOR; border-radius: 2px; }
.follow-up-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 4px;
    border-bottom: 1px solid BORDER_COLOR;
    transition: background 0.15s, padding-left 0.15s;
    cursor: default;
}
.follow-up-row:last-child { border-bottom: none; }
.follow-up-row:hover { padding-left: 10px; }
.follow-up-name {
    font-family: Fraunces, serif;
    font-size: 1.05rem;
    font-style: italic;
    color: TEXT_COLOR;
    font-weight: 300;
    margin-bottom: 3px;
    letter-spacing: -0.01em;
}
.follow-up-meta {
    font-family: JetBrains Mono, monospace;
    font-size: 0.48rem;
    letter-spacing: 0.14em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.follow-up-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
}
.follow-up-ago {
    font-family: JetBrains Mono, monospace;
    font-size: 0.46rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
</style>
'''

# Replace longer/specific placeholders first to avoid substring collisions.
# BG_COLOR is inside HOT_BG_COLOR / WARM_BG_COLOR / COLD_BG_COLOR.
# ACCENT_COLOR is inside ACCENT_WARM_COLOR and WARM_ACCENT_COLOR.
# TEXT_COLOR is inside TEXT_DIM_COLOR.
css = css.replace('HOT_BG_COLOR', HOT_BG)
css = css.replace('WARM_BG_COLOR', WARM_BG)
css = css.replace('COLD_BG_COLOR', COLD_BG)
css = css.replace('WARM_ACCENT_COLOR', WARM_ACCENT)
css = css.replace('ACCENT_WARM_COLOR', ACCENT_WARM)
css = css.replace('TEXT_DIM_COLOR', TEXT_DIM)
css = css.replace('CHART_LINE_COLOR', CHART_LINE)
css = css.replace('BG_COLOR', BG)
css = css.replace('PANEL_COLOR', PANEL)
css = css.replace('BORDER_COLOR', BORDER)
css = css.replace('TEXT_COLOR', TEXT)
css = css.replace('ACCENT_COLOR', ACCENT)
st.markdown(css, unsafe_allow_html=True)

# ======================================================
# TOP BAR
# ======================================================
now_time = datetime.now().strftime('%H:%M')
today_short = datetime.now().strftime('%Y%m%d').upper()

top_l, top_m, top_r = st.columns([3, 5, 1])
with top_l:
    st.markdown('<div class="lb-topbar-label">// LEADBOOST OS &nbsp; V3.0</div>', unsafe_allow_html=True)
with top_m:
    st.markdown('<div class="lb-topbar-label" style="text-align:center;">BOLIVIA &middot; ' + today_short + ' &middot; ' + now_time + '</div>', unsafe_allow_html=True)
with top_r:
    if st.button('DARK' if st.session_state.theme == 'light' else 'LIGHT', key='theme_toggle_dash'):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

# ======================================================
# PASSWORD
# ======================================================
OWNER_PASSWORD = 'leadboost2024'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    today_full = datetime.now().strftime('%A, %B %d, %Y').upper()
    hero = '<div class="lb-hero">'
    hero += '<div><div class="lb-hero-label">// DASHBOARD &middot; AGENTS ONLY</div>'
    hero += '<div class="lb-hero-title">Private <span class="lb-hero-accent">access</span>.</div></div>'
    hero += '<div class="lb-hero-right"><div class="lb-hero-date">BOLIVIA<br>' + now_time + '</div></div>'
    hero += '</div>'
    st.markdown(hero, unsafe_allow_html=True)
    pw = st.text_input('PASSWORD', type='password')
    if st.button('ENTER  //', type='primary'):
        if pw == OWNER_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error('Incorrect password.')
    st.stop()

# ======================================================
# DB FUNCTIONS
# ======================================================
@st.cache_resource
def get_supabase():
    return create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY'])

def load_leads():
    try:
        return get_supabase().table('leads').select('*').order('id', desc=True).execute().data
    except Exception as e:
        st.error('Error: ' + str(e))
        return []

def update_status(lead_id, new_status):
    try:
        data = {'status': new_status}
        if new_status == 'Contactado':
            data['contacted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        get_supabase().table('leads').update(data).eq('id', lead_id).execute()
    except Exception as e:
        st.error('Error: ' + str(e))

def get_minutes(lead):
    try:
        t1 = datetime.strptime(lead.get('timestamp', ''), '%Y-%m-%d %H:%M')
        t2 = datetime.strptime(lead.get('contacted_at', ''), '%Y-%m-%d %H:%M')
        m = int((t2 - t1).total_seconds() / 60)
        return m if m >= 0 else None
    except:
        return None

def fmt(minutes):
    if minutes is None: return '-'
    if minutes < 60: return str(minutes) + ' min'
    if minutes < 1440: return str(round(minutes / 60, 1)) + 'h'
    return str(round(minutes / 1440, 1)) + 'd'

def generate_excel(leads):
    wb = Workbook()
    ws = wb.active
    ws.title = 'LeadBoost'
    h_fill = PatternFill('solid', fgColor='1C1C1A')
    hot_f = PatternFill('solid', fgColor='EDD5CC')
    warm_f = PatternFill('solid', fgColor='E8DCC0')
    cold_f = PatternFill('solid', fgColor='D6D9CD')
    alt_f = PatternFill('solid', fgColor='FAF5E9')
    border = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC')
    )
    c = Alignment(horizontal='center', vertical='center')
    l = Alignment(horizontal='left', vertical='center')
    headers = ['#', 'Fecha', 'Nombre', 'Telefono', 'Tipo', 'Zona', 'Presupuesto', 'Plazo', 'Score', 'Estado', 'T. Respuesta']
    widths = [5, 18, 22, 15, 18, 18, 16, 12, 14, 14, 16]
    for i, (h, w) in enumerate(zip(headers, widths), 1):
        cell = ws.cell(row=1, column=i, value=h)
        cell.fill = h_fill
        cell.font = Font(bold=True, color='FFFFFF', size=11)
        cell.alignment = c
        cell.border = border
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 28
    for rn, lead in enumerate(leads, 2):
        score = lead.get('score', 'COLD')
        if score == 'HOT':
            row_fill = hot_f
        elif score == 'WARM':
            row_fill = warm_f
        else:
            row_fill = cold_f if rn % 2 == 0 else alt_f
        minutes = get_minutes(lead)
        row = [rn - 1, lead.get('timestamp', ''), lead.get('name', ''), lead.get('phone', ''),
               lead.get('property_type', ''), lead.get('area', ''), lead.get('budget', ''),
               lead.get('timeline', ''), score, lead.get('status', 'Nuevo'), fmt(minutes)]
        for cn, val in enumerate(row, 1):
            cell = ws.cell(row=rn, column=cn, value=val)
            cell.fill = row_fill
            cell.border = border
            cell.alignment = c if cn in [1, 7, 8, 9, 10, 11] else l
            cell.font = Font(bold=True, size=10) if cn == 3 else Font(size=10)
        ws.row_dimensions[rn].height = 22
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

# ======================================================
# COMPONENT HELPERS
# ======================================================
_sec_n = [0]
def sec_label(name, right_html=''):
    _sec_n[0] += 1
    num = str(_sec_n[0]).zfill(2)
    return ('<div class="section-label">'
            '<span class="section-label-left">'
            '<span class="section-num">' + num + '</span>'
            '<span class="section-sep">/</span>'
            '<span>' + name + '</span>'
            '</span>'
            + right_html + '</div>')

def expander_label(name, teaser=''):
    """Build an editorial expander summary string. Increments the section counter."""
    _sec_n[0] += 1
    num = str(_sec_n[0]).zfill(2)
    base = '//  ' + num + '   ·   ' + name
    if teaser:
        base += '   ·   ' + teaser
    return base

def daily_counts(leads_list, score_filter=None, days=30):
    today = datetime.now().date()
    dates = [(today - timedelta(days=days-1-i)).strftime('%Y-%m-%d') for i in range(days)]
    counts = {d: 0 for d in dates}
    for l in leads_list:
        if score_filter and l.get('score') != score_filter:
            continue
        ts = (l.get('timestamp') or '')[:10]
        if ts in counts:
            counts[ts] += 1
    return [counts[d] for d in dates]

def sparkline_svg(values, color, width=160, height=22):
    if not values:
        return ''
    max_v = max(values) if max(values) > 0 else 1
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = (i / (n - 1) * width) if n > 1 else width / 2
        y = height - (v / max_v * (height - 4)) - 2
        pts.append((round(x, 1), round(y, 1)))
    line = 'M' + ' L'.join(str(p[0]) + ',' + str(p[1]) for p in pts)
    area = line + ' L' + str(pts[-1][0]) + ',' + str(height) + ' L' + str(pts[0][0]) + ',' + str(height) + ' Z'
    return ('<svg width="100%" height="' + str(height) + '" viewBox="0 0 ' + str(width) + ' ' + str(height) + '" preserveAspectRatio="none" style="display:block;">'
            '<path d="' + area + '" fill="' + color + '" opacity="0.12"/>'
            '<path d="' + line + '" fill="none" stroke="' + color + '" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
            '</svg>')

def time_ago(ts_str):
    try:
        t = datetime.strptime(ts_str, '%Y-%m-%d %H:%M')
        delta = datetime.now() - t
        mins = int(delta.total_seconds() / 60)
        if mins < 60: return str(mins) + 'M AGO'
        if mins < 1440: return str(mins // 60) + 'H AGO'
        return str(mins // 1440) + 'D AGO'
    except:
        return ''

def heatmap_svg(leads_list, color, weeks=12):
    today = datetime.now().date()
    # Snap end-date to the most recent Sunday so each column is a clean Mon-Sun week
    today_dow = today.weekday()  # 0=Mon, 6=Sun
    days_to_sunday = (6 - today_dow) % 7
    end = today + timedelta(days=days_to_sunday)
    days = weeks * 7
    start = end - timedelta(days=days-1)  # this is a Monday

    counts = {}
    for l in leads_list:
        ts = (l.get('timestamp') or '')[:10]
        try:
            d = datetime.strptime(ts, '%Y-%m-%d').date()
            counts[d] = counts.get(d, 0) + 1
        except:
            continue
    max_count = max(counts.values()) if counts else 0

    cell = 18
    gap = 5
    label_col_w = 36   # space for day-of-week labels on the left
    label_row_h = 22   # space for month labels along the top

    grid_w = weeks * (cell + gap)
    grid_h = 7 * (cell + gap)
    total_w = label_col_w + grid_w
    total_h = label_row_h + grid_h

    svg = '<svg width="100%" height="' + str(total_h) + '" viewBox="0 0 ' + str(total_w) + ' ' + str(total_h) + '" preserveAspectRatio="xMidYMid meet" style="display:block;">'

    # Month labels along the top — only when month changes between weeks
    last_month = None
    for wi in range(weeks):
        sample = start + timedelta(days=wi * 7)
        if sample.month != last_month:
            x = label_col_w + wi * (cell + gap)
            svg += ('<text x="' + str(x) + '" y="' + str(label_row_h - 8)
                    + '" font-family="JetBrains Mono, monospace" font-size="9"'
                    + ' fill="' + TEXT_DIM + '" letter-spacing="1.6">'
                    + sample.strftime('%b').upper() + '</text>')
            last_month = sample.month

    # Day-of-week labels (left) — show Mon / Wed / Fri / Sun
    day_labels = ['MON', '', 'WED', '', 'FRI', '', 'SUN']
    for di, lbl in enumerate(day_labels):
        if not lbl:
            continue
        y = label_row_h + di * (cell + gap) + cell - 5
        svg += ('<text x="0" y="' + str(y)
                + '" font-family="JetBrains Mono, monospace" font-size="8.5"'
                + ' fill="' + TEXT_DIM + '" letter-spacing="1.2">' + lbl + '</text>')

    # Cells
    for wi in range(weeks):
        for di in range(7):
            i = wi * 7 + di
            day = start + timedelta(days=i)
            count = counts.get(day, 0)
            is_future = day > today
            if is_future:
                # Future cells: very faint, dashed feel
                opacity = 0.04
            elif max_count > 0 and count > 0:
                opacity = 0.25 + (count / max_count) * 0.75
            else:
                opacity = 0.10
            x = label_col_w + wi * (cell + gap)
            y = label_row_h + di * (cell + gap)
            svg += ('<rect x="' + str(x) + '" y="' + str(y)
                    + '" width="' + str(cell) + '" height="' + str(cell)
                    + '" rx="3" fill="' + color + '" opacity="' + str(round(opacity, 2)) + '">'
                    + '<title>' + day.strftime('%a %b %d') + ': ' + str(count) + ' lead' + ('s' if count != 1 else '') + '</title></rect>')

    svg += '</svg>'
    return svg

def pull_quote(text_html, attribution=''):
    html = '<div class="pull-quote">'
    html += '<div class="pull-quote-rule"></div>'
    html += '<div class="pull-quote-content">'
    html += '<div class="pull-quote-text">' + text_html + '</div>'
    if attribution:
        html += '<div class="pull-quote-attr">' + attribution + '</div>'
    html += '</div></div>'
    return html

def mini_stat(label, value, pct_text, sparkline_html='', accent=False):
    val_class = 'mini-stat-value mini-stat-value-accent' if accent else 'mini-stat-value'
    html = '<div class="mini-stat">'
    html += '<div class="mini-stat-left">'
    html += '<div class="mini-stat-label">' + label + '</div>'
    html += '<div class="' + val_class + '">' + str(value) + '</div>'
    html += '</div>'
    html += '<div class="mini-stat-right">'
    if sparkline_html:
        html += '<div class="mini-stat-spark">' + sparkline_html + '</div>'
    html += '<div class="mini-stat-pct">' + pct_text + '</div>'
    html += '</div>'
    html += '</div>'
    return html

def big_stat_card(label, value, delta_text, sparkline_full=''):
    html = '<div class="big-stat-card">'
    if sparkline_full:
        html += '<div class="big-stat-bg">' + sparkline_full + '</div>'
    html += '<div class="big-stat-content">'
    html += '<div class="big-stat-label">' + label + '</div>'
    html += '<div class="big-stat-num">' + str(value) + '</div>'
    html += '<div class="big-stat-delta">' + delta_text + '</div>'
    html += '</div>'
    html += '</div>'
    return html

def stat_card(label, value, sub, accent=False, top_class='stat-card-default', sparkline=''):
    val_class = 'stat-value-accent' if accent else 'stat-value'
    html = '<div class="stat-card ' + top_class + '">'
    html += '<div class="stat-label">' + label + '</div>'
    html += '<div class="' + val_class + '">' + str(value) + '</div>'
    if sparkline:
        html += '<div class="stat-spark">' + sparkline + '</div>'
    html += '<div class="stat-sub">' + sub + '</div>'
    html += '</div>'
    return html

def resp_card(label, value, sub, accent=False):
    val_class = 'stat-value-accent' if accent else 'stat-value'
    html = '<div class="resp-card">'
    html += '<div class="stat-label">' + label + '</div>'
    html += '<div class="' + val_class + '">' + str(value) + '</div>'
    html += '<div class="stat-sub">' + sub + '</div>'
    html += '</div>'
    return html

def score_ring_svg(hot, warm, cold, total):
    r = 22
    pi = 3.14159265
    c = round(2 * pi * r, 2)

    def seg(length, color, start):
        gap = round(c - length, 2)
        # Correct dashoffset: c - start places the segment at the right position
        offset = round(c - start, 2)
        return ('<circle cx="28" cy="28" r="' + str(r) + '" fill="none" stroke="' + color + '" stroke-width="5"'
                ' stroke-dasharray="' + str(length) + ' ' + str(gap) + '"'
                ' stroke-dashoffset="' + str(offset) + '"/>')

    svg = '<svg width="56" height="56" style="transform:rotate(-90deg);flex-shrink:0;">'
    svg += '<circle cx="28" cy="28" r="' + str(r) + '" fill="none" stroke="' + BORDER + '" stroke-width="5"/>'

    if total > 0:
        hot_len = round((hot / total) * c, 2)
        warm_len = round((warm / total) * c, 2)
        cold_len = round(c - hot_len - warm_len, 2)
        if cold_len > 0:
            svg += seg(cold_len, TEXT_DIM, hot_len + warm_len)
        if warm_len > 0:
            svg += seg(warm_len, WARM_ACCENT, hot_len)
        if hot_len > 0:
            svg += seg(hot_len, ACCENT_WARM, 0)

    svg += '</svg>'
    return svg

def funnel_strip(leads):
    statuses = ['Nuevo', 'Contactado', 'Visitado', 'Cerrado']
    counts = {s: sum(1 for l in leads if l.get('status', 'Nuevo') == s) for s in statuses}
    total = len(leads)
    html = '<div class="funnel-strip">'
    for i, s in enumerate(statuses):
        n = counts[s]
        pct = str(round(n / total * 100)) + '%' if total > 0 else '0%'
        html += '<div class="funnel-step">'
        html += '<div class="funnel-label">' + s + '</div>'
        html += '<div class="funnel-num">' + str(n) + '</div>'
        html += '<div class="funnel-pct">' + pct + ' of total</div>'
        html += '</div>'
        if i < len(statuses) - 1:
            html += '<div class="funnel-arrow">&#x2192;</div>'
    html += '</div>'
    return html

def zones_leaderboard(leads, top_n=6):
    from collections import Counter
    zone_counts = Counter(
        l.get('area', '').strip() for l in leads if l.get('area', '').strip()
    )
    top = zone_counts.most_common(top_n)
    if not top:
        return ''
    max_count = top[0][1]
    html = '<div class="zone-board">'
    for zone, count in top:
        bar_pct = round(count / max_count * 100)
        html += '<div class="zone-row">'
        html += '<div class="zone-name">' + zone + '</div>'
        html += '<div class="zone-bar-wrap"><div class="zone-bar" style="width:' + str(bar_pct) + '%"></div></div>'
        html += '<div class="zone-count">' + str(count) + '</div>'
        html += '</div>'
    html += '</div>'
    return html

# ======================================================
# LOAD DATA
# ======================================================
leads = load_leads()
total = len(leads)
hot = sum(1 for l in leads if l.get('score') == 'HOT')
warm = sum(1 for l in leads if l.get('score') == 'WARM')
cold = sum(1 for l in leads if l.get('score') == 'COLD')

def pct(n):
    if total == 0: return '0%'
    return str(round(n / total * 100)) + '%'

# ======================================================
# HERO
# ======================================================
hour = datetime.now().hour
if hour < 12:
    greeting_word = 'morning'
elif hour < 18:
    greeting_word = 'afternoon'
else:
    greeting_word = 'evening'

today_full = datetime.now().strftime('%A, %B %d, %Y').upper()
weekday_name = datetime.now().strftime('%A')
ring = score_ring_svg(hot, warm, cold, total)

# Briefing data
pending_count = sum(1 for l in leads if l.get('status', 'Nuevo') in ('Nuevo', 'Contactado'))
resp_minutes_list = [get_minutes(l) for l in leads]
resp_minutes_list = [m for m in resp_minutes_list if m is not None]
avg_resp = int(sum(resp_minutes_list) / len(resp_minutes_list)) if resp_minutes_list else None

from collections import Counter as _C
_zone_counts = _C(l.get('area', '').strip() for l in leads if l.get('area', '').strip())
_top_zone_pair = _zone_counts.most_common(1)
top_zone_name = _top_zone_pair[0][0] if _top_zone_pair else None

# Build briefing prose
briefing_parts = []
if hot > 0:
    briefing_parts.append('You have <span class="b-num-accent">' + str(hot) + '</span> hot lead' + ('s' if hot != 1 else ''))
elif total > 0:
    briefing_parts.append('You have <span class="b-num">' + str(total) + '</span> lead' + ('s' if total != 1 else '') + ' on file')
if pending_count > 0:
    briefing_parts.append('<span class="b-num">' + str(pending_count) + '</span> follow-up' + ('s' if pending_count != 1 else '') + ' pending')
if avg_resp is not None:
    briefing_parts.append('an average response of <span class="b-num">' + fmt(avg_resp) + '</span>')

briefing_main = ''
if briefing_parts:
    if len(briefing_parts) == 1:
        briefing_main = briefing_parts[0] + '.'
    elif len(briefing_parts) == 2:
        briefing_main = briefing_parts[0] + ' and ' + briefing_parts[1] + '.'
    else:
        briefing_main = ', '.join(briefing_parts[:-1]) + ', and ' + briefing_parts[-1] + '.'
else:
    briefing_main = 'No leads yet today — your dashboard is ready.'

briefing_zone = ''
if top_zone_name:
    briefing_zone = ' Top zone: <span class="b-place">' + top_zone_name + '</span>.'

hero = '<div class="lb-hero">'
hero += '<div style="flex:1;min-width:0;">'
hero += '<div class="lb-hero-label">// OPERATIONS PANEL &middot; LIVE</div>'
hero += '<div class="lb-hero-title">Good <span class="lb-hero-accent">' + greeting_word + '</span>.</div>'
hero += '<div class="lb-briefing">' + briefing_main + briefing_zone + '</div>'
hero += '</div>'
hero += '<div class="lb-hero-right">'
hero += '<div class="lb-hero-ring-wrap">'
hero += ring
hero += '<div class="lb-hero-ring-stats">'
hero += '<div class="lb-hero-ring-stat hot">&#x25CF; ' + str(hot) + ' hot</div>'
hero += '<div class="lb-hero-ring-stat">' + str(warm) + ' warm</div>'
hero += '<div class="lb-hero-ring-stat">' + str(cold) + ' cold</div>'
hero += '</div>'
hero += '</div>'
hero += '<div class="lb-hero-date">' + today_full + '<br>LOCAL TIME &middot; ' + now_time + '</div>'
hero += '</div>'
hero += '</div>'
st.markdown(hero, unsafe_allow_html=True)

# ======================================================
# TOP ACTIONS
# ======================================================
btn_refresh, btn_export, _ = st.columns([2, 2, 6])
with btn_refresh:
    if st.button('// REFRESH', key='refresh_btn'):
        st.cache_resource.clear()
        st.rerun()
with btn_export:
    if leads:
        st.download_button(
            label='EXPORT XLSX //',
            data=generate_excel(leads),
            file_name='leadboost_leads.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='export_btn'
        )

# ======================================================
# STATS
# ======================================================
st.markdown(sec_label('OVERVIEW', '<span class="section-count">' + str(total) + ' leads total</span>'), unsafe_allow_html=True)

# Sparklines for each score category
big_spark = sparkline_svg(daily_counts(leads), CHART_LINE, width=600, height=72)
hot_spark = sparkline_svg(daily_counts(leads, 'HOT'), ACCENT_WARM, width=110, height=22)
warm_spark = sparkline_svg(daily_counts(leads, 'WARM'), WARM_ACCENT, width=110, height=22)
cold_spark = sparkline_svg(daily_counts(leads, 'COLD'), TEXT_DIM, width=110, height=22)

# Compute "this week" delta for big stat
_today_d = datetime.now().date()
_week_start = _today_d - timedelta(days=6)
_this_week = sum(1 for l in leads if l.get('timestamp', '')[:10] >= _week_start.strftime('%Y-%m-%d'))
delta_text = '<span class="big-stat-delta-dim">LAST 7 DAYS &middot;</span> +' + str(_this_week) + ' NEW'

big_col, mini_col = st.columns([1, 1])
with big_col:
    st.markdown(big_stat_card('// TOTAL LEADS &middot; ALL TIME', total, delta_text, sparkline_full=big_spark), unsafe_allow_html=True)
with mini_col:
    stack = '<div class="mini-stat-stack">'
    stack += mini_stat('// HOT', hot, pct(hot) + ' OF TOTAL', sparkline_html=hot_spark, accent=True)
    stack += mini_stat('// WARM', warm, pct(warm) + ' OF TOTAL', sparkline_html=warm_spark)
    stack += mini_stat('// COLD', cold, pct(cold) + ' OF TOTAL', sparkline_html=cold_spark)
    stack += '</div>'
    st.markdown(stack, unsafe_allow_html=True)

# ======================================================
# PRE-COMPUTE METRICS FOR EXPANDER TEASERS + PULL-QUOTE
# ======================================================
if leads:
    _today_date = datetime.now().strftime('%Y-%m-%d')
    today_leads = sum(1 for l in leads if l.get('timestamp', '').startswith(_today_date))
    pending_contact = sum(1 for l in leads if l.get('status', 'Nuevo') == 'Nuevo')
    conv_rate = str(round((hot + warm) / total * 100)) + '%' if total > 0 else '0%'
    # Pipeline stage counts
    _stage_keys = ['Nuevo', 'Contactado', 'Visitado', 'Cerrado']
    _stage_counts = {k: sum(1 for l in leads if l.get('status', 'Nuevo') == k) for k in _stage_keys}
else:
    today_leads = 0
    pending_contact = 0
    conv_rate = '0%'
    _stage_counts = {}

# ======================================================
# PULL-QUOTE — always visible, surfaces the most striking metric
# ======================================================
quote_text = None
quote_attr = None
if total > 0:
    conv_n = round((hot + warm) / total * 100)
    if conv_n >= 50:
        quote_text = '<span class="pull-quote-text-accent">' + str(conv_n) + '%</span> of your leads are warm or hot — your best signal yet.'
        quote_attr = '// CONVERSION INSIGHT'
    elif hot >= 3:
        quote_text = '<span class="pull-quote-text-accent">' + str(hot) + ' hot leads</span> in the pipeline. Move fast — response time matters.'
        quote_attr = '// PRIORITY SIGNAL'
    elif top_zone_name and _top_zone_pair and _top_zone_pair[0][1] >= 2:
        quote_text = '<span class="pull-quote-text-accent">' + top_zone_name + '</span> leads the zones with ' + str(_top_zone_pair[0][1]) + ' leads. Worth doubling down.'
        quote_attr = '// MARKET FOCUS'
    elif resp_minutes_list and avg_resp is not None and avg_resp <= 30:
        quote_text = 'Average response time: <span class="pull-quote-text-accent">' + fmt(avg_resp) + '</span>. Fast enough to win.'
        quote_attr = '// PERFORMANCE'
    else:
        quote_text = 'Steady pipeline. <span class="pull-quote-text-accent">' + str(total) + '</span> leads on file, ' + str(pending_count) + ' still waiting on you.'
        quote_attr = '// OPERATIONS'
if quote_text:
    st.markdown(pull_quote(quote_text, quote_attr), unsafe_allow_html=True)

# ======================================================
# CONVERSION FUNNEL  (collapsible)
# ======================================================
if leads:
    _pipe_teaser = str(_stage_counts.get('Nuevo', 0)) + ' NEW · ' + str(_stage_counts.get('Contactado', 0)) + ' CONTACTED · ' + str(_stage_counts.get('Visitado', 0)) + ' VISITED · ' + str(_stage_counts.get('Cerrado', 0)) + ' CLOSED'
    with st.expander(expander_label('PIPELINE', _pipe_teaser), expanded=False):
        st.markdown(funnel_strip(leads), unsafe_allow_html=True)

# ======================================================
# CHARTS  (collapsible)
# ======================================================
if leads:
    with st.expander(expander_label('ANALYTICS', 'LEADS OVER TIME · BUDGET DISTRIBUTION'), expanded=False):
        ch1, ch2 = st.columns(2)

        with ch1:
            dates = [l.get('timestamp', '')[:10] for l in leads if l.get('timestamp')]
            if dates:
                df = pd.DataFrame({'date': dates})
                df['date'] = pd.to_datetime(df['date'])
                daily = df.groupby('date').size().reset_index(name='Leads').sort_values('date')

                base = alt.Chart(daily)

                area_layer = base.mark_area(
                    line={'color': CHART_LINE, 'strokeWidth': 2.2},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[
                            alt.GradientStop(color=CHART_FILL, offset=0),
                            alt.GradientStop(color=BG, offset=1)
                        ],
                        x1=1, x2=1, y1=1, y2=0
                    ),
                    interpolate='monotone',
                    opacity=0.95
                ).encode(
                    x=alt.X('date:T', axis=alt.Axis(
                        labelFont='JetBrains Mono',
                        labelFontSize=10,
                        labelColor=TEXT_DIM,
                        domainColor=BORDER,
                        tickColor=BORDER,
                        grid=False,
                        title=None,
                        format='%b %d',
                        labelAngle=0,
                        tickCount=6
                    )),
                    y=alt.Y('Leads:Q', axis=alt.Axis(
                        labelFont='JetBrains Mono',
                        labelFontSize=10,
                        labelColor=TEXT_DIM,
                        domainColor=BORDER,
                        tickColor=BORDER,
                        gridColor=BORDER,
                        gridOpacity=0.4,
                        title=None,
                        tickCount=4
                    ))
                )
                dot_layer = base.mark_point(
                    filled=True, size=50, color=CHART_LINE, strokeWidth=2, stroke=PANEL
                ).encode(x='date:T', y='Leads:Q')
                label_layer = base.mark_text(
                    font='JetBrains Mono', fontSize=10, color=CHART_LINE, dy=-13
                ).encode(x='date:T', y='Leads:Q', text='Leads:Q')

                area_chart = alt.layer(area_layer, dot_layer, label_layer).properties(
                    height=180, background='transparent'
                ).configure_view(strokeWidth=0)

                header = '<div class="chart-panel"><div class="chart-header">'
                header += '<div class="chart-title">// LEADS OVER TIME</div>'
                header += '<div class="chart-big-num">' + str(total) + ' total</div>'
                header += '</div>'
                st.markdown(header, unsafe_allow_html=True)
                st.altair_chart(area_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with ch2:
            def bucket(b):
                try:
                    v = int(str(b).replace(',', '').replace('.', '').replace('$', '').strip())
                    if v < 50000: return '< 50k'
                    if v < 100000: return '50-100k'
                    if v < 150000: return '100-150k'
                    return '> 150k'
                except:
                    return 'Unknown'

            order = ['< 50k', '50-100k', '100-150k', '> 150k']
            buckets = [bucket(l.get('budget', '0')) for l in leads]
            counts_df = pd.DataFrame({'Rango': buckets})
            counts_df = counts_df[counts_df['Rango'] != 'Unknown']
            if not counts_df.empty:
                counts_data = counts_df['Rango'].value_counts().reindex(order, fill_value=0).reset_index()
                counts_data.columns = ['Rango', 'Leads']

                bar_base = alt.Chart(counts_data)
                bar_layer = bar_base.mark_bar(
                    color=CHART_LINE,
                    opacity=0.92,
                    cornerRadiusTopLeft=3,
                    cornerRadiusTopRight=3
                ).encode(
                    x=alt.X('Rango:N', sort=order, axis=alt.Axis(
                        labelFont='JetBrains Mono',
                        labelFontSize=10,
                        labelColor=TEXT_DIM,
                        domainColor=BORDER,
                        tickColor=BORDER,
                        title=None,
                        labelAngle=0
                    )),
                    y=alt.Y('Leads:Q', axis=alt.Axis(
                        labelFont='JetBrains Mono',
                        labelFontSize=10,
                        labelColor=TEXT_DIM,
                        domainColor=BORDER,
                        tickColor=BORDER,
                        gridColor=BORDER,
                        gridOpacity=0.4,
                        title=None,
                        tickCount=4
                    ))
                )
                bar_label_layer = bar_base.mark_text(
                    font='JetBrains Mono', fontSize=11, color=CHART_LINE, dy=-8
                ).encode(
                    x=alt.X('Rango:N', sort=order),
                    y='Leads:Q',
                    text=alt.Text('Leads:Q')
                ).transform_filter(alt.datum.Leads > 0)

                bar_chart = alt.layer(bar_layer, bar_label_layer).properties(
                    height=180, background='transparent'
                ).configure_view(strokeWidth=0)

                header = '<div class="chart-panel"><div class="chart-header">'
                header += '<div class="chart-title">// BUDGET DISTRIBUTION</div>'
                header += '<div class="chart-big-num">USD ranges</div>'
                header += '</div>'
                st.markdown(header, unsafe_allow_html=True)
                st.altair_chart(bar_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# CADENCE — calendar heatmap of daily lead volume
# ======================================================
if leads:
    # Compute busiest day for the explanation
    _hm_busiest_count = 0
    _hm_busiest_day = None
    for l in leads:
        ts = (l.get('timestamp') or '')[:10]
        try:
            d = datetime.strptime(ts, '%Y-%m-%d').date()
            c = sum(1 for _l in leads if (_l.get('timestamp') or '')[:10] == ts)
            if c > _hm_busiest_count:
                _hm_busiest_count = c
                _hm_busiest_day = d
        except:
            continue
    busiest_text = ''
    if _hm_busiest_day:
        busiest_text = _hm_busiest_day.strftime('%b %d').upper() + ' &middot; ' + str(_hm_busiest_count) + ' LEAD' + ('S' if _hm_busiest_count != 1 else '')

    _cad_teaser = str(total) + ' LEADS OVER 12 WEEKS'
    with st.expander(expander_label('CADENCE', _cad_teaser), expanded=False):
        hm_svg = heatmap_svg(leads, ACCENT_WARM, weeks=12)
        hm_html = '<div class="heatmap-wrap">'
        hm_html += '<div class="heatmap-header">'
        hm_html += '<div class="heatmap-title-block">'
        hm_html += '<div class="heatmap-title">// DAILY LEAD VOLUME</div>'
        hm_html += '<div class="heatmap-subtitle">Each square is a day. Darker squares mean more leads received on that day.</div>'
        hm_html += '</div>'
        hm_html += '<div class="heatmap-meta-block">'
        hm_html += '<div class="heatmap-meta">' + str(total) + ' over 84 days</div>'
        if busiest_text:
            hm_html += '<div class="heatmap-busiest">BUSIEST &middot; ' + busiest_text + '</div>'
        hm_html += '</div>'
        hm_html += '</div>'
        hm_html += '<div class="heatmap-svg-wrap">' + hm_svg + '</div>'
        # Mini legend
        hm_html += '<div class="heatmap-legend"><span>LESS</span>'
        hm_html += '<span class="heatmap-legend-cells">'
        for op in [0.10, 0.30, 0.50, 0.72, 1.0]:
            hm_html += '<span class="heatmap-legend-cell" style="opacity:' + str(op) + ';"></span>'
        hm_html += '</span><span>MORE</span></div>'
        hm_html += '</div>'
        st.markdown(hm_html, unsafe_allow_html=True)

# ======================================================
# DAILY STATS  (collapsible)
# ======================================================
if leads:
    _today_teaser = str(today_leads) + ' NEW · ' + str(pending_contact) + ' PENDING · ' + conv_rate + ' CONVERSION'
    with st.expander(expander_label('TODAY', _today_teaser), expanded=False):
        d1, d2, d3 = st.columns(3)
        with d1: st.markdown(stat_card('// TODAY\'S LEADS', today_leads, 'RECEIVED TODAY'), unsafe_allow_html=True)
        with d2: st.markdown(stat_card('// PENDING CONTACT', pending_contact, 'NEED FOLLOW-UP', accent=True), unsafe_allow_html=True)
        with d3: st.markdown(stat_card('// CONVERSION RATE', conv_rate, 'HOT + WARM / TOTAL'), unsafe_allow_html=True)

# ======================================================
# TOP ZONES + FOLLOW-UPS
# ======================================================
def follow_up_panel(leads_list):
    pending = [l for l in leads_list if l.get('status', 'Nuevo') in ('Nuevo', 'Contactado')]
    pending = sorted(pending, key=lambda l: l.get('timestamp', ''), reverse=True)
    html = '<div class="chart-panel"><div class="chart-header">'
    html += '<div class="chart-title">// FOLLOW-UPS</div>'
    html += '<div class="chart-big-num" style="color:' + ACCENT_WARM + ';font-size:1.15rem;">' + str(len(pending)) + ' pending</div>'
    html += '</div>'
    if not pending:
        html += '<div style="font-family:JetBrains Mono,monospace;font-size:0.5rem;color:' + TEXT_DIM + ';letter-spacing:0.16em;padding:20px 0;text-align:center;">ALL LEADS CONTACTED.</div>'
    else:
        html += '<div class="follow-up-list">'
        for l in pending:
            st_val = l.get('status', 'Nuevo')
            sc = l.get('score', 'COLD')
            nm = l.get('name', '-')
            prop = l.get('property_type', '')
            bgt = l.get('budget', '-')
            ago = time_ago(l.get('timestamp', ''))
            html += '<div class="follow-up-row">'
            html += '<div>'
            html += '<div class="follow-up-name">' + nm + '</div>'
            html += '<div class="follow-up-meta">' + st_val.upper() + ' &middot; ' + prop.upper() + ' &middot; $' + str(bgt) + '</div>'
            html += '</div>'
            html += '<div class="follow-up-right">'
            html += '<span class="badge score-' + sc.lower() + '">' + sc + '</span>'
            if ago:
                html += '<span class="follow-up-ago">' + ago + '</span>'
            html += '</div>'
            html += '</div>'
        html += '</div>'
    html += '</div>'
    return html

if leads:
    _z_teaser = ('TOP: ' + top_zone_name.upper()) if top_zone_name else 'ZONES'
    _z_teaser += ' · ' + str(pending_count) + ' FOLLOW-UPS PENDING'
    with st.expander(expander_label('ZONES & FOLLOW-UPS', _z_teaser), expanded=False):
        zones_html = zones_leaderboard(leads)
        zl, zr = st.columns(2)
        with zl:
            if zones_html:
                header = '<div class="chart-panel"><div class="chart-header">'
                header += '<div class="chart-title">// TOP ZONES</div>'
                header += '<div class="chart-big-num">by lead count</div>'
                header += '</div>'
                st.markdown(header + zones_html + '</div>', unsafe_allow_html=True)
        with zr:
            st.markdown(follow_up_panel(leads), unsafe_allow_html=True)

# ======================================================
# RESPONSE TIME  (collapsible)
# ======================================================
timed_full = [{'name': l.get('name', '-'), 'minutes': get_minutes(l)} for l in leads if get_minutes(l) is not None]
if timed_full:
    avg = sum(t['minutes'] for t in timed_full) / len(timed_full)
    fastest = min(timed_full, key=lambda x: x['minutes'])
    slowest = max(timed_full, key=lambda x: x['minutes'])
    _rt_teaser = 'AVG ' + fmt(int(avg)) + ' · FASTEST ' + fmt(fastest['minutes']) + ' · ' + str(len(timed_full)) + ' CONTACTED'
    with st.expander(expander_label('RESPONSE TIME', _rt_teaser), expanded=False):
        t1, t2, t3 = st.columns(3)
        with t1: st.markdown(resp_card('// AVG RESPONSE', fmt(int(avg)), 'ACROSS ' + str(len(timed_full)) + ' LEADS'), unsafe_allow_html=True)
        with t2: st.markdown(resp_card('// FASTEST', fmt(fastest['minutes']), fastest['name'].upper(), accent=True), unsafe_allow_html=True)
        with t3: st.markdown(resp_card('// SLOWEST', fmt(slowest['minutes']), slowest['name'].upper()), unsafe_allow_html=True)

# ======================================================
# SEARCH + FILTERS
# ======================================================
st.markdown(sec_label('LEADS'), unsafe_allow_html=True)

search_col, f1, f2 = st.columns([3, 1, 1])
with search_col:
    search = st.text_input('// SEARCH', placeholder='Name or phone number', label_visibility='collapsed')
with f1:
    filter_score = st.selectbox('// SCORE', ['All', 'HOT', 'WARM', 'COLD'])
with f2:
    filter_status = st.selectbox('// STATUS', ['All', 'Nuevo', 'Contactado', 'Visitado', 'Cerrado'])

filtered = leads
if search.strip():
    q = search.strip().lower()
    filtered = [l for l in filtered if q in l.get('name', '').lower() or q in l.get('phone', '').lower()]
if filter_score != 'All':
    filtered = [l for l in filtered if l.get('score') == filter_score]
if filter_status != 'All':
    filtered = [l for l in filtered if l.get('status', 'Nuevo') == filter_status]

leads_hdr_badges = ('<span class="badge score-hot" style="margin-left:6px;">HOT ' + str(hot) + '</span>'
                    '<span class="badge score-warm" style="margin-left:5px;">WARM ' + str(warm) + '</span>'
                    '<span class="badge score-cold" style="margin-left:5px;">COLD ' + str(cold) + '</span>')
st.markdown(
    '<div style="display:flex;justify-content:space-between;align-items:center;'
    'margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid ' + BORDER + ';">'
    '<div style="font-family:JetBrains Mono,monospace;font-size:0.55rem;letter-spacing:0.22em;color:' + TEXT_DIM + ';">'
    '// LEADS &nbsp;&middot;&nbsp; ' + str(len(filtered)) + ' SHOWING</div>'
    '<div>' + leads_hdr_badges + '</div>'
    '</div>',
    unsafe_allow_html=True
)

# ======================================================
# LEAD CARDS
# ======================================================
if not filtered:
    st.markdown('<div class="empty-state">No leads match your filters.</div>', unsafe_allow_html=True)
else:
    statuses_list = ['Nuevo', 'Contactado', 'Visitado', 'Cerrado']
    for lead in filtered:
        lead_id = lead.get('id')
        score = lead.get('score', 'COLD')
        status = lead.get('status', 'Nuevo')
        name = lead.get('name', '-')
        phone = lead.get('phone', '').replace('+', '').replace(' ', '').replace('-', '')
        ptype = lead.get('property_type', '')
        area = lead.get('area', '')
        budget = lead.get('budget', '-')
        timeline = lead.get('timeline', '-')
        ts = lead.get('timestamp', '-')
        minutes = get_minutes(lead)

        if score == 'HOT':
            score_badge = ('<span style="position:relative;display:inline-flex;align-items:center;">'
                           '<span style="position:absolute;inset:0;border-radius:20px;background:' + ACCENT_WARM + ';animation:lb-hot-pulse 2s ease-out infinite;pointer-events:none;"></span>'
                           '<span class="badge score-hot">HOT</span>'
                           '</span>')
        else:
            score_badge = '<span class="badge score-' + score.lower() + '">' + score + '</span>'
        status_badge = '<span class="badge">' + status.upper() + '</span>'
        resp_html = ''
        if minutes is not None:
            resp_html = '<span class="resp-time">' + fmt(minutes) + ' &nbsp;</span>'

        wa_msg = 'Hola ' + name + ', soy de la agencia inmobiliaria LeadBoost. Te contactamos porque mostraste interes en ' + ptype + ' en ' + area + '. Tienes un momento para hablar?'
        wa_link = 'https://wa.me/591' + phone + '?text=' + quote(wa_msg)

        card = '<div class="lead-card lead-card-' + score.lower() + '">'
        card += '<div class="lead-top">'
        card += '<span class="lead-name">' + name + '</span>'
        card += '<div class="lead-badges">' + resp_html + status_badge + '&nbsp;' + score_badge + '</div>'
        card += '</div>'
        card += '<div class="lead-grid">'
        card += '<div><span class="field-label">// PHONE</span>' + str(lead.get('phone', '-')) + '</div>'
        card += '<div><span class="field-label">// PROPERTY</span>' + ptype + '</div>'
        card += '<div><span class="field-label">// LOCATION</span>' + area + '</div>'
        card += '<div><span class="field-label">// BUDGET</span>$' + str(budget) + '</div>'
        card += '<div><span class="field-label">// TIMELINE</span>' + str(timeline) + ' meses</div>'
        card += '<div><span class="field-label">// SCORE</span>' + score + '</div>'
        card += '</div>'
        card += '<div class="lead-footer">'
        card += '<span class="lead-ts">// RECEIVED &middot; ' + str(ts) + '</span>'
        card += '<a class="wa-btn" href="' + wa_link + '" target="_blank">// WHATSAPP</a>'
        card += '</div>'
        card += '</div>'
        st.markdown(card, unsafe_allow_html=True)

        status_cols = st.columns(4)
        for si, s in enumerate(statuses_list):
            with status_cols[si]:
                is_current = status == s
                if st.button(s.upper(), key='s_' + str(lead_id) + '_' + s, disabled=is_current):
                    update_status(lead_id, s)
                    st.rerun()

        current_note = lead.get('notes') or ''
        note_input = st.text_area(
            '// NOTES',
            value=current_note,
            key='note_' + str(lead_id),
            placeholder='Add agent notes here...',
            height=64,
            label_visibility='visible'
        )
        if st.button('SAVE NOTE', key='save_note_' + str(lead_id)):
            try:
                get_supabase().table('leads').update({'notes': note_input}).eq('id', lead_id).execute()
                st.success('Saved.')
                st.rerun()
            except Exception as e:
                st.error('Error: ' + str(e))

        st.markdown('<div style="margin-bottom:16px"></div>', unsafe_allow_html=True)

# ======================================================
# LOGOUT + FOOTER
# ======================================================
st.markdown('<div style="border-top:1px solid ' + BORDER + ';margin-top:28px;padding-top:18px;"></div>', unsafe_allow_html=True)
foot_l, foot_r = st.columns([2, 5])
with foot_l:
    if st.button('// LOG OUT'):
        st.session_state.authenticated = False
        st.rerun()
with foot_r:
    today_ver = datetime.now().strftime('%Y-%m-%d')
    st.markdown(
        '<div style="padding-top:10px;font-family:JetBrains Mono,monospace;font-size:0.48rem;'
        'color:' + TEXT_DIM + ';letter-spacing:0.14em;text-align:right;">'
        'LEADBOOST OS &middot; V3.0 &middot; ' + today_ver + '</div>',
        unsafe_allow_html=True
    )
