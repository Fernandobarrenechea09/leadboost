import streamlit as st
from supabase import create_client
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from urllib.parse import quote
import pandas as pd
import altair as alt

# ======================================================

# PAGE CONFIG

# ======================================================

st.set_page_config(
page_title=‘LEADBOOST DASHBOARD’,
page_icon=’#’,
layout=‘wide’,
initial_sidebar_state=‘collapsed’
)

# ======================================================

# THEME STATE

# ======================================================

if ‘theme’ not in st.session_state:
st.session_state.theme = ‘light’

# ======================================================

# THEME COLORS

# ======================================================

if st.session_state.theme == ‘light’:
BG = ‘#F2EDE2’
PANEL = ‘#FAF5E9’
BORDER = ‘#D8D0BC’
TEXT = ‘#1C1C1A’
TEXT_DIM = ‘#8A8473’
ACCENT = ‘#1C1C1A’
ACCENT_WARM = ‘#C4633F’
CHART_FILL = ‘#E8C9A8’
CHART_LINE = ‘#C4633F’
HOT_BG = ‘#EDD5CC’
WARM_BG = ‘#E8DCC0’
COLD_BG = ‘#D6D9CD’
else:
BG = ‘#18150F’
PANEL = ‘#221E16’
BORDER = ‘#3A342A’
TEXT = ‘#EDE6D4’
TEXT_DIM = ‘#8A8473’
ACCENT = ‘#EDE6D4’
ACCENT_WARM = ‘#D47A4D’
CHART_FILL = ‘#4A3826’
CHART_LINE = ‘#D47A4D’
HOT_BG = ‘#3A2820’
WARM_BG = ‘#332B1E’
COLD_BG = ‘#252420’

# ======================================================

# CSS

# ======================================================

css = ‘’’

<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp, .main {
    font-family: Inter, sans-serif;
    background-color: BG_COLOR !important;
    color: TEXT_COLOR !important;
}
.stApp { background-color: BG_COLOR !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1280px !important; }

.lb-topbar-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    padding-top: 18px;
}

.lb-hero {
    border: 1px solid BORDER_COLOR;
    background: PANEL_COLOR;
    border-radius: 14px;
    padding: 26px 30px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.lb-hero-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.lb-hero-title {
    font-family: Fraunces, serif;
    font-size: 2.8rem;
    color: TEXT_COLOR;
    line-height: 1;
    font-style: italic;
    font-weight: 400;
    letter-spacing: -0.02em;
}
.lb-hero-accent { color: ACCENT_WARM_COLOR; }
.lb-hero-date {
    font-family: JetBrains Mono, monospace;
    font-size: 0.65rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.12em;
    text-align: right;
    line-height: 1.7;
}

.stat-card {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 18px 22px;
    height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.stat-label {
    font-family: JetBrains Mono, monospace;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.stat-value {
    font-family: Fraunces, serif;
    font-size: 2.8rem;
    color: TEXT_COLOR;
    line-height: 1;
    font-style: italic;
    font-weight: 400;
    letter-spacing: -0.02em;
}
.stat-value-accent {
    font-family: Fraunces, serif;
    font-size: 2.8rem;
    color: ACCENT_WARM_COLOR;
    line-height: 1;
    font-style: italic;
    font-weight: 400;
    letter-spacing: -0.02em;
}
.stat-sub {
    font-family: JetBrains Mono, monospace;
    font-size: 0.6rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.12em;
}

.chart-panel {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 18px 22px 10px 22px;
    margin-bottom: 10px;
}
.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid BORDER_COLOR;
}
.chart-title {
    font-family: JetBrains Mono, monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.chart-big-num {
    font-family: Fraunces, serif;
    font-size: 1.2rem;
    color: TEXT_COLOR;
    font-style: italic;
}

.badge {
    font-family: JetBrains Mono, monospace;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid BORDER_COLOR;
    text-transform: uppercase;
    font-weight: 500;
    color: TEXT_COLOR;
    display: inline-block;
}
.score-hot { background: HOT_BG_COLOR; }
.score-warm { background: WARM_BG_COLOR; }
.score-cold { background: COLD_BG_COLOR; }

.lead-card {
    background: PANEL_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 4px;
}
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
    font-size: 1.4rem;
    font-style: italic;
    color: TEXT_COLOR;
    font-weight: 400;
}
.lead-badges { display: flex; gap: 8px; align-items: center; }
.lead-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px 28px;
    font-family: JetBrains Mono, monospace;
    font-size: 0.76rem;
    color: TEXT_COLOR;
    margin-bottom: 14px;
}
.field-label {
    color: TEXT_DIM_COLOR;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    display: block;
    margin-bottom: 3px;
}
.wa-btn {
    display: inline-block;
    background: ACCENT_COLOR;
    color: BG_COLOR;
    padding: 9px 20px;
    border-radius: 8px;
    text-decoration: none;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.resp-time {
    font-family: JetBrains Mono, monospace;
    font-size: 0.62rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.1em;
}

.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: PANEL_COLOR !important;
    color: TEXT_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 8px !important;
    font-family: Inter, sans-serif !important;
}
.stSelectbox > div > div {
    background: PANEL_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 8px !important;
}
.stTextInput label, .stSelectbox label, .stTextArea label {
    color: TEXT_DIM_COLOR !important;
    font-family: JetBrains Mono, monospace !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}

div.stButton > button {
    background: ACCENT_COLOR;
    color: BG_COLOR;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    transition: all 0.15s;
}
div.stButton > button:hover { opacity: 0.85; }
div.stButton > button:disabled { opacity: 0.35; }
div.stDownloadButton > button {
    background: ACCENT_COLOR;
    color: BG_COLOR;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

.theme-btn-wrap div.stButton > button {
    background: transparent !important;
    color: TEXT_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    padding: 4px 12px !important;
    font-size: 0.58rem !important;
    border-radius: 20px !important;
}

header { visibility: hidden; height: 0; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>

‘’’

css = css.replace(‘BG_COLOR’, BG)
css = css.replace(‘PANEL_COLOR’, PANEL)
css = css.replace(‘BORDER_COLOR’, BORDER)
css = css.replace(‘TEXT_DIM_COLOR’, TEXT_DIM)
css = css.replace(‘TEXT_COLOR’, TEXT)
css = css.replace(‘ACCENT_WARM_COLOR’, ACCENT_WARM)
css = css.replace(‘ACCENT_COLOR’, ACCENT)
css = css.replace(‘HOT_BG_COLOR’, HOT_BG)
css = css.replace(‘WARM_BG_COLOR’, WARM_BG)
css = css.replace(‘COLD_BG_COLOR’, COLD_BG)
st.markdown(css, unsafe_allow_html=True)

# ======================================================

# TOP BAR

# ======================================================

now_time = datetime.now().strftime(’%H:%M’)
today_short = datetime.now().strftime(’%Y%m%d’).upper()

top_l, top_m, top_r = st.columns([3, 5, 1])
with top_l:
st.markdown(’<div class="lb-topbar-label">// LEADBOOST OS   V3.0</div>’, unsafe_allow_html=True)
with top_m:
st.markdown(’<div class="lb-topbar-label" style="text-align:center;">BOLIVIA · ’ + today_short + ’ · ’ + now_time + ‘</div>’, unsafe_allow_html=True)
with top_r:
st.markdown(’<div class="theme-btn-wrap" style="padding-top:12px;">’, unsafe_allow_html=True)
if st.button(‘Dark’ if st.session_state.theme == ‘light’ else ‘Light’, key=‘theme_toggle_dash’):
st.session_state.theme = ‘dark’ if st.session_state.theme == ‘light’ else ‘light’
st.rerun()
st.markdown(’</div>’, unsafe_allow_html=True)

# ======================================================

# PASSWORD

# ======================================================

OWNER_PASSWORD = ‘leadboost2024’
if ‘authenticated’ not in st.session_state:
st.session_state.authenticated = False

if not st.session_state.authenticated:
today_full = datetime.now().strftime(’%A, %B %d, %Y’).upper()
hero = ‘<div class="lb-hero">’
hero += ‘<div><div class="lb-hero-label">// DASHBOARD · AGENTS ONLY</div>’
hero += ‘<div class="lb-hero-title">Private <span class="lb-hero-accent">access</span>.</div></div>’
hero += ‘<div class="lb-hero-date">BOLIVIA<br>’ + now_time + ‘</div></div>’
st.markdown(hero, unsafe_allow_html=True)
pw = st.text_input(‘PASSWORD’, type=‘password’)
if st.button(‘ENTER  //’):
if pw == OWNER_PASSWORD:
st.session_state.authenticated = True
st.rerun()
else:
st.error(‘Incorrect password.’)
st.stop()

# ======================================================

# HERO

# ======================================================

today_full = datetime.now().strftime(’%A, %B %d, %Y’).upper()
hero = ‘<div class="lb-hero">’
hero += ‘<div><div class="lb-hero-label">// OPERATIONS PANEL · LIVE</div>’
hero += ‘<div class="lb-hero-title">Good <span class="lb-hero-accent">afternoon</span>.</div></div>’
hero += ‘<div class="lb-hero-date">’ + today_full + ’<br>LOCAL TIME · ’ + now_time + ‘</div></div>’
st.markdown(hero, unsafe_allow_html=True)

# ======================================================

# DB FUNCTIONS

# ======================================================

@st.cache_resource
def get_supabase():
return create_client(st.secrets[‘SUPABASE_URL’], st.secrets[‘SUPABASE_KEY’])

def load_leads():
try:
return get_supabase().table(‘leads’).select(’*’).order(‘id’, desc=True).execute().data
except Exception as e:
st.error(’Error: ’ + str(e))
return []

def update_status(lead_id, new_status):
try:
data = {‘status’: new_status}
if new_status == ‘Contactado’:
data[‘contacted_at’] = datetime.now().strftime(’%Y-%m-%d %H:%M’)
get_supabase().table(‘leads’).update(data).eq(‘id’, lead_id).execute()
except Exception as e:
st.error(’Error: ’ + str(e))

def get_minutes(lead):
try:
t1 = datetime.strptime(lead.get(‘timestamp’, ‘’), ‘%Y-%m-%d %H:%M’)
t2 = datetime.strptime(lead.get(‘contacted_at’, ‘’), ‘%Y-%m-%d %H:%M’)
m = int((t2 - t1).total_seconds() / 60)
return m if m >= 0 else None
except:
return None

def fmt(minutes):
if minutes is None: return ‘-’
if minutes < 60: return str(minutes) + ’ min’
if minutes < 1440: return str(round(minutes/60, 1)) + ‘h’
return str(round(minutes/1440, 1)) + ‘d’

def generate_excel(leads):
wb = Workbook()
ws = wb.active
ws.title = ‘LeadBoost’
h_fill = PatternFill(‘solid’, fgColor=‘1C1C1A’)
hot_f = PatternFill(‘solid’, fgColor=‘EDD5CC’)
warm_f = PatternFill(‘solid’, fgColor=‘E8DCC0’)
cold_f = PatternFill(‘solid’, fgColor=‘D6D9CD’)
alt_f = PatternFill(‘solid’, fgColor=‘FAF5E9’)
border = Border(
left=Side(style=‘thin’, color=‘CCCCCC’),
right=Side(style=‘thin’, color=‘CCCCCC’),
top=Side(style=‘thin’, color=‘CCCCCC’),
bottom=Side(style=‘thin’, color=‘CCCCCC’)
)
c = Alignment(horizontal=‘center’, vertical=‘center’)
l = Alignment(horizontal=‘left’, vertical=‘center’)
headers = [’#’, ‘Fecha’, ‘Nombre’, ‘Telefono’, ‘Tipo’, ‘Zona’, ‘Presupuesto’, ‘Plazo’, ‘Score’, ‘Estado’, ‘T. Respuesta’]
widths = [5, 18, 22, 15, 18, 18, 16, 12, 14, 14, 16]
for i, (h, w) in enumerate(zip(headers, widths), 1):
cell = ws.cell(row=1, column=i, value=h)
cell.fill = h_fill
cell.font = Font(bold=True, color=‘FFFFFF’, size=11)
cell.alignment = c
cell.border = border
ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 28
for rn, lead in enumerate(leads, 2):
score = lead.get(‘score’, ‘COLD’)
if score == ‘HOT’:
row_fill = hot_f
elif score == ‘WARM’:
row_fill = warm_f
else:
row_fill = cold_f if rn % 2 == 0 else alt_f
minutes = get_minutes(lead)
row = [rn - 1, lead.get(‘timestamp’, ‘’), lead.get(‘name’, ‘’), lead.get(‘phone’, ‘’),
lead.get(‘property_type’, ‘’), lead.get(‘area’, ‘’), lead.get(‘budget’, ‘’),
lead.get(‘timeline’, ‘’), score, lead.get(‘status’, ‘Nuevo’), fmt(minutes)]
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

# LOAD LEADS

# ======================================================

leads = load_leads()

# ======================================================

# TOP ACTIONS

# ======================================================

b1, b2, _ = st.columns([1, 1, 6])
with b1:
if st.button(’// REFRESH’):
st.cache_resource.clear()
st.rerun()
with b2:
if leads:
st.download_button(
label=‘EXPORT XLSX  //’,
data=generate_excel(leads),
file_name=‘leadboost_leads.xlsx’,
mime=‘application/vnd.openxmlformats-officedocument.spreadsheetml.sheet’
)

st.markdown(’<div style="margin-top:14px"></div>’, unsafe_allow_html=True)

# ======================================================

# STATS

# ======================================================

total = len(leads)
hot = sum(1 for l in leads if l.get(‘score’) == ‘HOT’)
warm = sum(1 for l in leads if l.get(‘score’) == ‘WARM’)
cold = sum(1 for l in leads if l.get(‘score’) == ‘COLD’)

def pct(n):
if total == 0: return ‘0%’
return str(round(n / total * 100)) + ‘%’

def stat_card(label, value, sub, accent=False):
val_class = ‘stat-value-accent’ if accent else ‘stat-value’
html = ‘<div class="stat-card">’
html += ‘<div class="stat-label">’ + label + ‘</div>’
html += ‘<div class="' + val_class + '">’ + str(value) + ‘</div>’
html += ‘<div class="stat-sub">’ + sub + ‘</div>’
html += ‘</div>’
return html

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(stat_card(’// TOTAL LEADS’, total, ‘ALL TIME’), unsafe_allow_html=True)
with c2: st.markdown(stat_card(’// HOT’, hot, pct(hot) + ’ OF TOTAL’, accent=True), unsafe_allow_html=True)
with c3: st.markdown(stat_card(’// WARM’, warm, pct(warm) + ’ OF TOTAL’), unsafe_allow_html=True)
with c4: st.markdown(stat_card(’// COLD’, cold, pct(cold) + ’ OF TOTAL’), unsafe_allow_html=True)

st.markdown(’<div style="margin-top:14px"></div>’, unsafe_allow_html=True)

# ======================================================

# CHARTS

# ======================================================

if leads:
ch1, ch2 = st.columns(2)

```
with ch1:
    dates = [l.get('timestamp', '')[:10] for l in leads if l.get('timestamp')]
    if dates:
        df = pd.DataFrame({'date': dates})
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby('date').size().reset_index(name='Leads').sort_values('date')

        area_chart = alt.Chart(daily).mark_area(
            line={'color': CHART_LINE, 'strokeWidth': 2},
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color=CHART_FILL, offset=0),
                    alt.GradientStop(color=BG, offset=1)
                ],
                x1=1, x2=1, y1=1, y2=0
            ),
            interpolate='monotone'
        ).encode(
            x=alt.X('date:T', axis=alt.Axis(
                labelFont='JetBrains Mono',
                labelFontSize=9,
                labelColor=TEXT_DIM,
                domainColor=BORDER,
                tickColor=BORDER,
                title=None,
                format='%b %d',
                labelAngle=0
            )),
            y=alt.Y('Leads:Q', axis=alt.Axis(
                labelFont='JetBrains Mono',
                labelFontSize=9,
                labelColor=TEXT_DIM,
                domainColor=BORDER,
                tickColor=BORDER,
                gridColor=BORDER,
                title=None,
                tickCount=4
            ))
        ).properties(height=200, background=PANEL).configure_view(strokeWidth=0)

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

    order = ['< 50k', '50-100k', '100-150k', '> 150k', 'Unknown']
    buckets = [bucket(l.get('budget', '0')) for l in leads]
    counts = pd.DataFrame({'Rango': buckets})['Rango'].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ['Rango', 'Leads']

    bar_chart = alt.Chart(counts).mark_bar(
        color=CHART_LINE,
        opacity=0.85,
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X('Rango:N', sort=order, axis=alt.Axis(
            labelFont='JetBrains Mono',
            labelFontSize=9,
            labelColor=TEXT_DIM,
            domainColor=BORDER,
            tickColor=BORDER,
            title=None,
            labelAngle=0
        )),
        y=alt.Y('Leads:Q', axis=alt.Axis(
            labelFont='JetBrains Mono',
            labelFontSize=9,
            labelColor=TEXT_DIM,
            domainColor=BORDER,
            tickColor=BORDER,
            gridColor=BORDER,
            title=None,
            tickCount=4
        ))
    ).properties(height=200, background=PANEL).configure_view(strokeWidth=0)

    header = '<div class="chart-panel"><div class="chart-header">'
    header += '<div class="chart-title">// BUDGET DISTRIBUTION</div>'
    header += '<div class="chart-big-num">USD ranges</div>'
    header += '</div>'
    st.markdown(header, unsafe_allow_html=True)
    st.altair_chart(bar_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
```

# ======================================================

# RESPONSE TIME

# ======================================================

timed = [{‘name’: l.get(‘name’, ‘-’), ‘minutes’: get_minutes(l)} for l in leads if get_minutes(l) is not None]
if timed:
avg = sum(t[‘minutes’] for t in timed) / len(timed)
fastest = min(timed, key=lambda x: x[‘minutes’])
slowest = max(timed, key=lambda x: x[‘minutes’])
t1, t2, t3 = st.columns(3)
with t1: st.markdown(stat_card(’// AVG RESPONSE’, fmt(int(avg)), ‘ACROSS ’ + str(len(timed)) + ’ LEADS’), unsafe_allow_html=True)
with t2: st.markdown(stat_card(’// FASTEST’, fmt(fastest[‘minutes’]), fastest[‘name’].upper(), accent=True), unsafe_allow_html=True)
with t3: st.markdown(stat_card(’// SLOWEST’, fmt(slowest[‘minutes’]), slowest[‘name’].upper()), unsafe_allow_html=True)
st.markdown(’<div style="margin-top:14px"></div>’, unsafe_allow_html=True)

# ======================================================

# SEARCH + FILTERS

# ======================================================

search = st.text_input(’// SEARCH BY NAME OR PHONE’, placeholder=‘Carlos or 76543210’)
f1, f2 = st.columns(2)
with f1: filter_score = st.selectbox(’// FILTER BY SCORE’, [‘Todos’, ‘HOT’, ‘WARM’, ‘COLD’])
with f2: filter_status = st.selectbox(’// FILTER BY STATUS’, [‘Todos’, ‘Nuevo’, ‘Contactado’, ‘Visitado’, ‘Cerrado’])

filtered = leads
if search.strip():
q = search.strip().lower()
filtered = [l for l in filtered if q in l.get(‘name’, ‘’).lower() or q in l.get(‘phone’, ‘’).lower()]
if filter_score != ‘Todos’:
filtered = [l for l in filtered if l.get(‘score’) == filter_score]
if filter_status != ‘Todos’:
filtered = [l for l in filtered if l.get(‘status’, ‘Nuevo’) == filter_status]

# ======================================================

# LEADS

# ======================================================

st.markdown(’<div style="font-family: JetBrains Mono, monospace; font-size:0.6rem; letter-spacing:0.2em; color:' + TEXT_DIM + '; text-transform:uppercase; margin-top:20px; margin-bottom:8px;">// LEADS  ·  ’ + str(len(filtered)) + ’ SHOWING</div>’, unsafe_allow_html=True)

if not filtered:
st.markdown(’<div class="chart-panel"><div class="chart-title">No leads to show.</div></div>’, unsafe_allow_html=True)
else:
for lead in filtered:
lead_id = lead.get(‘id’)
score = lead.get(‘score’, ‘COLD’)
status = lead.get(‘status’, ‘Nuevo’)
name = lead.get(‘name’, ‘-’)
phone = lead.get(‘phone’, ‘’).replace(’+’, ‘’).replace(’ ‘, ‘’).replace(’-’, ‘’)
ptype = lead.get(‘property_type’, ‘’)
area = lead.get(‘area’, ‘’)
budget = lead.get(‘budget’, ‘-’)
timeline = lead.get(‘timeline’, ‘-’)
ts = lead.get(‘timestamp’, ‘-’)
minutes = get_minutes(lead)

```
    score_badge = '<span class="badge score-' + score.lower() + '">' + score + '</span>'
    status_badge = '<span class="badge">' + status.upper() + '</span>'
    resp_html = ''
    if minutes is not None:
        resp_html = '<span class="resp-time">' + fmt(minutes) + '</span>'

    wa_msg = 'Hola ' + name + ', soy de la agencia inmobiliaria LeadBoost. Te contactamos porque mostraste interes en ' + ptype + ' en ' + area + '. Tienes un momento para hablar?'
    wa_link = 'https://wa.me/591' + phone + '?text=' + quote(wa_msg)

    card = '<div class="lead-card">'
    card += '<div class="lead-top">'
    card += '<span class="lead-name">' + name + '</span>'
    card += '<div class="lead-badges">' + resp_html + status_badge + score_badge + '</div>'
    card += '</div>'
    card += '<div class="lead-grid">'
    card += '<div><span class="field-label">// PHONE</span>' + str(lead.get('phone', '-')) + '</div>'
    card += '<div><span class="field-label">// PROPERTY</span>' + ptype + '</div>'
    card += '<div><span class="field-label">// LOCATION</span>' + area + '</div>'
    card += '<div><span class="field-label">// BUDGET</span>$' + str(budget) + '</div>'
    card += '<div><span class="field-label">// TIMELINE</span>' + str(timeline) + ' meses</div>'
    card += '<div><span class="field-label">// RECEIVED</span>' + str(ts) + '</div>'
    card += '</div>'
    card += '<a class="wa-btn" href="' + wa_link + '" target="_blank">// WHATSAPP</a>'
    card += '</div>'
    st.markdown(card, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, s in enumerate(['Nuevo', 'Contactado', 'Visitado', 'Cerrado']):
        with cols[i]:
            is_current = status == s
            label = ('[X] ' + s.upper()) if is_current else s.upper()
            if st.button(label, key='s_' + str(lead_id) + '_' + s, disabled=is_current):
                update_status(lead_id, s)
                st.rerun()

    current_note = lead.get('notes') or ''
    note_input = st.text_area('// AGENT NOTES', value=current_note, key='note_' + str(lead_id),
                              placeholder='Llame dos veces, no contesto...', height=70)
    if st.button('SAVE NOTE  //', key='save_note_' + str(lead_id)):
        try:
            get_supabase().table('leads').update({'notes': note_input}).eq('id', lead_id).execute()
            st.success('Saved.')
            st.rerun()
        except Exception as e:
            st.error('Error: ' + str(e))

    st.markdown('<div style="margin-bottom:20px"></div>', unsafe_allow_html=True)
```

# ======================================================

# LOGOUT

# ======================================================

st.markdown(’<div style="border-top:1px solid ' + BORDER + '; margin-top:30px; padding-top:20px;"></div>’, unsafe_allow_html=True)
if st.button(’// LOG OUT’):
st.session_state.authenticated = False
st.rerun()
