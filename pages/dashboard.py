import streamlit as st
from supabase import create_client
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from urllib.parse import quote
import pandas as pd

# ─────────────────────────────────────────────

# PAGE CONFIG

# ─────────────────────────────────────────────

st.set_page_config(
page_title=“LEADBOOST // DASHBOARD”,
page_icon=“■”,
layout=“wide”
)

# ─────────────────────────────────────────────

# THEME STATE

# ─────────────────────────────────────────────

if “theme” not in st.session_state:
st.session_state.theme = “light”

# ─────────────────────────────────────────────

# THEME TOGGLE (TOP RIGHT)

# ─────────────────────────────────────────────

col_spacer, col_toggle = st.columns([11, 1])
with col_toggle:
if st.button(“☾” if st.session_state.theme == “light” else “☀”, key=“theme_toggle_dash”):
st.session_state.theme = “dark” if st.session_state.theme == “light” else “light”
st.rerun()

# ─────────────────────────────────────────────

# THEME COLORS

# ─────────────────────────────────────────────

if st.session_state.theme == “light”:
BG       = “#F5F1E8”
PANEL    = “#FFFFFF”
BORDER   = “#D4CFC0”
TEXT     = “#1A1A1A”
TEXT_DIM = “#6B6B6B”
ACCENT   = “#1A1A1A”
HOT_BG   = “#F5E1DC”
WARM_BG  = “#F5EDD6”
COLD_BG  = “#E3E8ED”
else:
BG       = “#0F0F0F”
PANEL    = “#1A1A1A”
BORDER   = “#2A2A2A”
TEXT     = “#F0F0F0”
TEXT_DIM = “#8A8A8A”
ACCENT   = “#F0F0F0”
HOT_BG   = “#3A1F1F”
WARM_BG  = “#3A2E1F”
COLD_BG  = “#1F2A35”

# ─────────────────────────────────────────────

# CUSTOM CSS

# ─────────────────────────────────────────────

st.markdown(f”””

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp, .main {{
    font-family: 'Inter', sans-serif;
    background-color: {BG} !important;
    color: {TEXT} !important;
}}
.stApp {{ background-color: {BG} !important; }}

/* Panels */
.panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 14px;
}}
.panel-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    color: {TEXT_DIM};
    text-transform: uppercase;
    margin-bottom: 8px;
}}

/* Header */
.lb-header {{
    border: 1px solid {BORDER};
    background: {PANEL};
    border-radius: 4px;
    padding: 18px 24px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.lb-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: {TEXT};
    line-height: 1;
    margin: 4px 0 0 0;
    font-style: italic;
}}
.lb-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {TEXT_DIM};
    letter-spacing: 0.1em;
    text-align: right;
}}

/* Stats */
.stat-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 16px 20px;
}}
.stat-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    color: {TEXT_DIM};
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.stat-value {{
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: {TEXT};
    line-height: 1;
    font-style: italic;
}}
.stat-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {TEXT_DIM};
    margin-top: 4px;
}}

/* Score + Status badges */
.badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    padding: 4px 10px;
    border-radius: 2px;
    border: 1px solid {BORDER};
    text-transform: uppercase;
    font-weight: 500;
}}
.score-hot  {{ background:{HOT_BG};  color:{TEXT}; border-color: {TEXT_DIM}; }}
.score-warm {{ background:{WARM_BG}; color:{TEXT}; border-color: {TEXT_DIM}; }}
.score-cold {{ background:{COLD_BG}; color:{TEXT}; border-color: {TEXT_DIM}; }}
.status-b   {{ background: transparent; color: {TEXT}; }}

/* Lead card */
.lead-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 18px 22px;
    margin-bottom: 4px;
}}
.lead-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid {BORDER};
}}
.lead-name {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    font-style: italic;
    color: {TEXT};
}}
.lead-badges {{ display: flex; gap: 8px; align-items: center; }}
.lead-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: {TEXT};
    margin-bottom: 14px;
}}
.lead-grid .field-label {{
    color: {TEXT_DIM};
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    display: block;
    margin-bottom: 2px;
}}
.wa-btn {{
    display: inline-block;
    background: {ACCENT};
    color: {BG};
    padding: 8px 18px;
    border-radius: 2px;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}}
.resp-time {{
    font-family: 'JetBrains Mono', monospace;
    font-size:0.65rem;
    color:{TEXT_DIM};
    letter-spacing: 0.1em;
}}

/* Inputs */
.stTextInput > div > div > input, .stTextArea > div > div > textarea {{
    background: {PANEL} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 2px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}}
.stSelectbox > div > div {{
    background: {PANEL} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 2px !important;
}}
.stTextInput label, .stSelectbox label, .stTextArea label {{
    color: {TEXT_DIM} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}}

div.stButton > button {{
    background: {ACCENT};
    color: {BG};
    border: none;
    border-radius: 2px;
    padding: 9px 22px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}}
div.stButton > button:hover {{ opacity: 0.85; }}
div.stButton > button:disabled {{ opacity: 0.35; }}
div.stDownloadButton > button {{
    background: {ACCENT};
    color: {BG};
    border: none;
    border-radius: 2px;
    padding: 9px 22px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}}

h3 {{
    font-family: 'DM Serif Display', serif !important;
    font-style: italic !important;
    color: {TEXT} !important;
    font-weight: 400 !important;
}}

header {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
</style>

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# PASSWORD GATE

# ─────────────────────────────────────────────

OWNER_PASSWORD = “leadboost2024”

if “authenticated” not in st.session_state:
st.session_state.authenticated = False

if not st.session_state.authenticated:
st.markdown(f”””
<div class="lb-header">
<div>
<div class="panel-label">■ LEADBOOST // DASHBOARD</div>
<div class="lb-title">Private access.</div>
</div>
<div class="lb-sub">AGENTS ONLY · BOLIVIA</div>
</div>
“””, unsafe_allow_html=True)

```
st.markdown('<div class="panel-label">PASSWORD</div>', unsafe_allow_html=True)
password_input = st.text_input("pw", type="password", label_visibility="collapsed")
if st.button("ENTER →"):
    if password_input == OWNER_PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.error("Incorrect password.")
st.stop()
```

# ─────────────────────────────────────────────

# SUPABASE

# ─────────────────────────────────────────────

@st.cache_resource
def get_supabase():
return create_client(st.secrets[“SUPABASE_URL”], st.secrets[“SUPABASE_KEY”])

def load_leads():
try:
return get_supabase().table(“leads”).select(”*”).order(“id”, desc=True).execute().data
except Exception as e:
st.error(f”Error: {e}”)
return []

def update_status(lead_id, new_status):
try:
data = {“status”: new_status}
if new_status == “Contactado”:
data[“contacted_at”] = datetime.now().strftime(”%Y-%m-%d %H:%M”)
get_supabase().table(“leads”).update(data).eq(“id”, lead_id).execute()
except Exception as e:
st.error(f”Error: {e}”)

# ─────────────────────────────────────────────

# TIME HELPERS

# ─────────────────────────────────────────────

def get_minutes(lead):
try:
t1 = datetime.strptime(lead.get(“timestamp”, “”),    “%Y-%m-%d %H:%M”)
t2 = datetime.strptime(lead.get(“contacted_at”, “”), “%Y-%m-%d %H:%M”)
m  = int((t2 - t1).total_seconds() / 60)
return m if m >= 0 else None
except:
return None

def fmt(minutes):
if minutes is None: return “—”
if minutes < 60:    return f”{minutes} min”
if minutes < 1440:  return f”{round(minutes/60,1)}h”
return f”{round(minutes/1440,1)}d”

# ─────────────────────────────────────────────

# EXCEL EXPORT

# ─────────────────────────────────────────────

def generate_excel(leads):
wb = Workbook()
ws = wb.active
ws.title = “LeadBoost”
h_fill = PatternFill(“solid”, fgColor=“1A1A1A”)
hot_f  = PatternFill(“solid”, fgColor=“F5E1DC”)
warm_f = PatternFill(“solid”, fgColor=“F5EDD6”)
cold_f = PatternFill(“solid”, fgColor=“E3E8ED”)
alt_f  = PatternFill(“solid”, fgColor=“FAF7EE”)
border = Border(left=Side(style=“thin”,color=“CCCCCC”), right=Side(style=“thin”,color=“CCCCCC”),
top=Side(style=“thin”,color=“CCCCCC”), bottom=Side(style=“thin”,color=“CCCCCC”))
c = Alignment(horizontal=“center”, vertical=“center”)
l = Alignment(horizontal=“left”,   vertical=“center”)
headers = [”#”,“Fecha”,“Nombre”,“Telefono”,“Tipo”,“Zona”,“Presupuesto”,“Plazo”,“Score”,“Estado”,“T. Respuesta”]
widths  = [5,18,22,15,18,18,16,12,14,14,16]
for i,(h,w) in enumerate(zip(headers,widths),1):
cell = ws.cell(row=1,column=i,value=h)
cell.fill=h_fill; cell.font=Font(bold=True,color=“FFFFFF”,size=11)
cell.alignment=c; cell.border=border
ws.column_dimensions[get_column_letter(i)].width=w
ws.row_dimensions[1].height=28
for rn,lead in enumerate(leads,2):
score = lead.get(“score”,“COLD”)
row_fill = hot_f if score==“HOT” else warm_f if score==“WARM” else (cold_f if rn%2==0 else alt_f)
minutes = get_minutes(lead)
row = [rn-1, lead.get(“timestamp”,””), lead.get(“name”,””), lead.get(“phone”,””),
lead.get(“property_type”,””), lead.get(“area”,””), lead.get(“budget”,””),
lead.get(“timeline”,””), score, lead.get(“status”,“Nuevo”), fmt(minutes)]
for cn,val in enumerate(row,1):
cell=ws.cell(row=rn,column=cn,value=val)
cell.fill=row_fill; cell.border=border
cell.alignment=c if cn in [1,7,8,9,10,11] else l
cell.font=Font(bold=True,size=10) if cn==3 else Font(size=10)
ws.row_dimensions[rn].height=22
buf=io.BytesIO(); wb.save(buf); buf.seek(0)
return buf

# ─────────────────────────────────────────────

# HEADER

# ─────────────────────────────────────────────

now_str = datetime.now().strftime(”%H:%M”)
today   = datetime.now().strftime(”%A, %B %d, %Y”).upper()

st.markdown(f”””

<div class="lb-header">
  <div>
    <div class="panel-label">■ LEADBOOST // DASHBOARD · V3.0</div>
    <div class="lb-title">Operations panel.</div>
  </div>
  <div class="lb-sub">{today}<br>BOLIVIA · {now_str}</div>
</div>
""", unsafe_allow_html=True)

leads = load_leads()

# ─────────────────────────────────────────────

# TOP ACTIONS

# ─────────────────────────────────────────────

b1, b2, _ = st.columns([1, 1, 6])
with b1:
if st.button(“↻ REFRESH”):
st.cache_resource.clear()
st.rerun()
with b2:
if leads:
st.download_button(
label=“↓ EXPORT XLSX”,
data=generate_excel(leads),
file_name=“leadboost_leads.xlsx”,
mime=“application/vnd.openxmlformats-officedocument.spreadsheetml.sheet”
)

# ─────────────────────────────────────────────

# STATS

# ─────────────────────────────────────────────

total = len(leads)
hot   = sum(1 for l in leads if l.get(“score”)==“HOT”)
warm  = sum(1 for l in leads if l.get(“score”)==“WARM”)
cold  = sum(1 for l in leads if l.get(“score”)==“COLD”)
pct   = lambda n: f”{round(n/total*100)}%” if total else “0%”

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(f’<div class="stat-card"><div class="stat-label">TOTAL LEADS</div><div class="stat-value">{total}</div><div class="stat-sub">ALL TIME</div></div>’, unsafe_allow_html=True)
with c2: st.markdown(f’<div class="stat-card"><div class="stat-label">HOT</div><div class="stat-value">{hot}</div><div class="stat-sub">{pct(hot)} OF TOTAL</div></div>’, unsafe_allow_html=True)
with c3: st.markdown(f’<div class="stat-card"><div class="stat-label">WARM</div><div class="stat-value">{warm}</div><div class="stat-sub">{pct(warm)} OF TOTAL</div></div>’, unsafe_allow_html=True)
with c4: st.markdown(f’<div class="stat-card"><div class="stat-label">COLD</div><div class="stat-value">{cold}</div><div class="stat-sub">{pct(cold)} OF TOTAL</div></div>’, unsafe_allow_html=True)

st.markdown(”<br>”, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# CHARTS — two columns

# ─────────────────────────────────────────────

if leads:
ch1, ch2 = st.columns(2)

```
with ch1:
    st.markdown('<div class="panel-label">■ LEADS OVER TIME</div>', unsafe_allow_html=True)
    dates = [l.get("timestamp","")[:10] for l in leads if l.get("timestamp")]
    if dates:
        df = pd.DataFrame({"fecha": dates})
        df["fecha"] = pd.to_datetime(df["fecha"])
        chart_data = df.groupby("fecha").size().reset_index(name="Leads").sort_values("fecha").rename(columns={"fecha":"Fecha"})
        st.line_chart(chart_data.set_index("Fecha"), height=240)

with ch2:
    st.markdown('<div class="panel-label">■ BUDGET DISTRIBUTION</div>', unsafe_allow_html=True)
    def bucket(b):
        try:
            v = int(str(b).replace(",","").replace(".","").replace("$","").strip())
            if v < 50000:   return "< $50k"
            if v < 100000:  return "$50–100k"
            if v < 150000:  return "$100–150k"
            return "> $150k"
        except:
            return "Unknown"
    order   = ["< $50k","$50–100k","$100–150k","> $150k","Unknown"]
    buckets = [bucket(l.get("budget","0")) for l in leads]
    counts  = pd.DataFrame({"Rango": buckets})["Rango"].value_counts().reindex(order, fill_value=0)
    st.bar_chart(counts, height=240)
```

st.markdown(”<br>”, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# RESPONSE TIME

# ─────────────────────────────────────────────

timed = [{“name”: l.get(“name”,”—”), “minutes”: get_minutes(l)} for l in leads if get_minutes(l) is not None]
if timed:
avg     = sum(t[“minutes”] for t in timed) / len(timed)
fastest = min(timed, key=lambda x: x[“minutes”])
slowest = max(timed, key=lambda x: x[“minutes”])
t1,t2,t3 = st.columns(3)
with t1: st.markdown(f’<div class="stat-card"><div class="stat-label">AVG RESPONSE</div><div class="stat-value">{fmt(int(avg))}</div><div class="stat-sub">ACROSS {len(timed)} LEADS</div></div>’, unsafe_allow_html=True)
with t2: st.markdown(f’<div class="stat-card"><div class="stat-label">FASTEST</div><div class="stat-value">{fmt(fastest[“minutes”])}</div><div class="stat-sub">{fastest[“name”].upper()}</div></div>’, unsafe_allow_html=True)
with t3: st.markdown(f’<div class="stat-card"><div class="stat-label">SLOWEST</div><div class="stat-value">{fmt(slowest[“minutes”])}</div><div class="stat-sub">{slowest[“name”].upper()}</div></div>’, unsafe_allow_html=True)
st.markdown(”<br>”, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# SEARCH + FILTERS

# ─────────────────────────────────────────────

search = st.text_input(“SEARCH BY NAME OR PHONE”, placeholder=“Carlos · 76543210”)
f1,f2 = st.columns(2)
with f1: filter_score  = st.selectbox(“FILTER BY SCORE”,  [“Todos”,“HOT”,“WARM”,“COLD”])
with f2: filter_status = st.selectbox(“FILTER BY STATUS”, [“Todos”,“Nuevo”,“Contactado”,“Visitado”,“Cerrado”])

filtered = leads
if search.strip():
q = search.strip().lower()
filtered = [l for l in filtered if q in l.get(“name”,””).lower() or q in l.get(“phone”,””).lower()]
if filter_score  != “Todos”: filtered = [l for l in filtered if l.get(“score”)==filter_score]
if filter_status != “Todos”: filtered = [l for l in filtered if l.get(“status”,“Nuevo”)==filter_status]

# ─────────────────────────────────────────────

# LEADS LIST

# ─────────────────────────────────────────────

st.markdown(f’<div class="panel-label" style="margin-top:24px;">■ LEADS · {len(filtered)} SHOWING</div>’, unsafe_allow_html=True)

if not filtered:
st.markdown(f’<div class="panel"><div class="panel-label">No leads to show.</div></div>’, unsafe_allow_html=True)
else:
for lead in filtered:
lead_id  = lead.get(“id”)
score    = lead.get(“score”,“COLD”)
status   = lead.get(“status”,“Nuevo”)
name     = lead.get(“name”,”—”)
phone    = lead.get(“phone”,””).replace(”+”,””).replace(” “,””).replace(”-”,””)
ptype    = lead.get(“property_type”,””)
area     = lead.get(“area”,””)
budget   = lead.get(“budget”,”—”)
timeline = lead.get(“timeline”,”—”)
ts       = lead.get(“timestamp”,”—”)
minutes  = get_minutes(lead)

```
    score_badge  = f'<span class="badge score-{score.lower()}">◆ {score}</span>'
    status_badge = f'<span class="badge status-b">● {status.upper()}</span>'
    resp_html    = f'<span class="resp-time">· {fmt(minutes)}</span>' if minutes is not None else ""

    wa_msg  = f"Hola {name}, soy de la agencia inmobiliaria LeadBoost. Te contactamos porque mostraste interes en {ptype} en {area}. Tienes un momento para hablar?"
    wa_link = f"https://wa.me/591{phone}?text={quote(wa_msg)}"

    st.markdown(f"""
```

<div class="lead-card">
  <div class="lead-top">
    <span class="lead-name">{name}</span>
    <div class="lead-badges">{resp_html}{status_badge}{score_badge}</div>
  </div>
  <div class="lead-grid">
    <div><span class="field-label">PHONE</span>{lead.get('phone','—')}</div>
    <div><span class="field-label">PROPERTY</span>{ptype}</div>
    <div><span class="field-label">LOCATION</span>{area}</div>
    <div><span class="field-label">BUDGET</span>${budget}</div>
    <div><span class="field-label">TIMELINE</span>{timeline} meses</div>
    <div><span class="field-label">RECEIVED</span>{ts}</div>
  </div>
  <a class="wa-btn" href="{wa_link}" target="_blank">→ WHATSAPP</a>
</div>
""", unsafe_allow_html=True)

```
    cols = st.columns(4)
    for i,s in enumerate(["Nuevo","Contactado","Visitado","Cerrado"]):
        with cols[i]:
            is_current = status == s
            if st.button(f"✓ {s.upper()}" if is_current else s.upper(), key=f"s_{lead_id}_{s}", disabled=is_current):
                update_status(lead_id, s)
                st.rerun()

    current_note = lead.get("notes") or ""
    note_input = st.text_area("AGENT NOTES", value=current_note, key=f"note_{lead_id}",
                               placeholder="Llame dos veces, no contesto...", height=80)
    if st.button("SAVE NOTE", key=f"save_note_{lead_id}"):
        try:
            get_supabase().table("leads").update({"notes": note_input}).eq("id", lead_id).execute()
            st.success("Saved.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
```

# ─────────────────────────────────────────────

# LOGOUT

# ─────────────────────────────────────────────

st.markdown(”—”)
if st.button(“⏻ LOG OUT”):
st.session_state.authenticated = False
st.rerun()
