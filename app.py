import streamlit as st
from supabase import create_client
from datetime import datetime
import anthropic
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title='LEADBOOST',
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
    BUBBLE_BOT = '#FAF5E9'
    BUBBLE_USR = '#1C1C1A'
    BUBBLE_USR_TXT = '#F2EDE2'
else:
    BG = '#18150F'
    PANEL = '#221E16'
    BORDER = '#3A342A'
    TEXT = '#EDE6D4'
    TEXT_DIM = '#8A8473'
    ACCENT = '#EDE6D4'
    ACCENT_WARM = '#D47A4D'
    BUBBLE_BOT = '#221E16'
    BUBBLE_USR = '#EDE6D4'
    BUBBLE_USR_TXT = '#18150F'

# ======================================================
# CSS
# ======================================================
css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp, .main {
    font-family: Inter, sans-serif;
    background-color: BG_COLOR !important;
    color: TEXT_COLOR !important;
}
.stApp { background-color: BG_COLOR !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px !important; }

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
    padding: 28px 32px;
    margin-bottom: 14px;
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
    margin-bottom: 6px;
}
.lb-hero-title {
    font-family: Fraunces, serif;
    font-size: 3rem;
    color: TEXT_COLOR;
    line-height: 1;
    font-style: italic;
    font-weight: 400;
    letter-spacing: -0.02em;
}
.lb-hero-accent { color: ACCENT_WARM_COLOR; }
.lb-hero-date {
    font-family: JetBrains Mono, monospace;
    font-size: 0.68rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.12em;
    text-align: right;
    line-height: 1.7;
}

.chat-wrap { display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px; }
.bubble-bot {
    background: BUBBLE_BOT_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 4px 16px 16px 16px;
    padding: 14px 18px;
    max-width: 78%;
    align-self: flex-start;
    font-size: 0.94rem;
    line-height: 1.6;
    color: TEXT_COLOR;
}
.bubble-user {
    background: BUBBLE_USR_COLOR;
    color: BUBBLE_USR_TXT_COLOR;
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    max-width: 78%;
    align-self: flex-end;
    font-size: 0.94rem;
    line-height: 1.6;
}
.label-row {
    font-family: JetBrains Mono, monospace;
    font-size: 0.58rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.label-user { text-align: right; }

.stTextInput > div > div > input {
    background: PANEL_COLOR !important;
    color: TEXT_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 8px !important;
    padding: 13px 16px !important;
    font-family: Inter, sans-serif !important;
    font-size: 0.94rem !important;
}
.stTextInput label {
    color: TEXT_DIM_COLOR !important;
    font-family: JetBrains Mono, monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
}

div.stButton > button {
    background: ACCENT_COLOR;
    color: BG_COLOR;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-family: JetBrains Mono, monospace;
    font-weight: 500;
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.15s;
}
div.stButton > button:hover { opacity: 0.85; }
div.stButton > button:disabled { opacity: 0.35; }

.theme-btn-wrap div.stButton > button {
    background: transparent !important;
    color: TEXT_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    padding: 4px 12px !important;
    font-size: 0.62rem !important;
    border-radius: 20px !important;
}

header { visibility: hidden; height: 0; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
'''

css = css.replace('BG_COLOR', BG)
css = css.replace('PANEL_COLOR', PANEL)
css = css.replace('BORDER_COLOR', BORDER)
css = css.replace('TEXT_DIM_COLOR', TEXT_DIM)
css = css.replace('TEXT_COLOR', TEXT)
css = css.replace('ACCENT_WARM_COLOR', ACCENT_WARM)
css = css.replace('ACCENT_COLOR', ACCENT)
css = css.replace('BUBBLE_BOT_COLOR', BUBBLE_BOT)
css = css.replace('BUBBLE_USR_COLOR', BUBBLE_USR)
css = css.replace('BUBBLE_USR_TXT_COLOR', BUBBLE_USR_TXT)
st.markdown(css, unsafe_allow_html=True)

# ======================================================
# TOP BAR
# ======================================================
now_time = datetime.now().strftime('%H:%M')
today_short = datetime.now().strftime('%Y%m%d').upper()

top_l, top_m, top_r = st.columns([3, 4, 1])
with top_l:
    st.markdown('<div class="lb-topbar-label">// LEADBOOST &nbsp; V3.0</div>', unsafe_allow_html=True)
with top_m:
    st.markdown('<div class="lb-topbar-label" style="text-align:center;">BOLIVIA &middot; ' + today_short + ' &middot; ' + now_time + '</div>', unsafe_allow_html=True)
with top_r:
    st.markdown('<div class="theme-btn-wrap" style="padding-top:12px;">', unsafe_allow_html=True)
    if st.button('Dark' if st.session_state.theme == 'light' else 'Light', key='theme_toggle'):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# HERO
# ======================================================
today_full = datetime.now().strftime('%A, %B %d, %Y').upper()
hero = '<div class="lb-hero">'
hero += '<div>'
hero += '<div class="lb-hero-label">// WELCOME &middot; REAL ESTATE ASSISTANT</div>'
hero += '<div class="lb-hero-title">Good <span class="lb-hero-accent">day</span>.</div>'
hero += '</div>'
hero += '<div class="lb-hero-date">' + today_full + '<br>LOCAL TIME &middot; ' + now_time + '</div>'
hero += '</div>'
st.markdown(hero, unsafe_allow_html=True)

# ======================================================
# CONNECTIONS
# ======================================================
@st.cache_resource
def get_supabase():
    return create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY'])

@st.cache_resource
def get_claude():
    return anthropic.Anthropic(api_key=st.secrets['ANTHROPIC_KEY'])

# ======================================================
# SYSTEM PROMPT
# ======================================================
SYSTEM_PROMPT = '''Eres LeadBoost, un asistente inmobiliario virtual para agencias de bienes raices en Bolivia. Tu trabajo es recopilar exactamente 6 datos del usuario mediante una conversacion natural en espanol.

Los 6 datos son:
1. Nombre completo
2. Tipo de propiedad (Casa, Departamento, Terreno, Local comercial)
3. Zona o barrio
4. Presupuesto en dolares (solo numero, ejemplo: 150000)
5. Plazo en meses (solo numero, ejemplo: 2)
6. Telefono

FASE 1 - RECOPILACION: Conversa naturalmente. Si el usuario da varios datos en un mensaje extraelos todos. Pregunta solo lo que falta.

FASE 2 - CONFIRMACION: Con los 6 datos muestra:

Perfecto, antes de finalizar dejame confirmar tu informacion:

Nombre: [nombre]
Tipo de propiedad: [tipo]
Zona: [zona]
Presupuesto: [presupuesto]
Plazo: [plazo] meses
Telefono: [telefono]

Es correcta toda esta informacion?

FASE 3 - CIERRE: Cuando confirme responde EXACTAMENTE:

Gracias [nombre]! Hemos registrado tu informacion correctamente. En breve uno de nuestros agentes se pondra en contacto contigo.
LEAD_COMPLETO:{"name":"...","property_type":"...","area":"...","budget":"150000","timeline":"2","phone":"..."}

IMPORTANTE: budget y timeline son solo numeros.'''

# ======================================================
# SESSION STATE
# ======================================================
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'messages' not in st.session_state: st.session_state.messages = []
if 'done' not in st.session_state: st.session_state.done = False
if 'greeted' not in st.session_state: st.session_state.greeted = False

# ======================================================
# SCORING
# ======================================================
def score_lead(lead):
    try:
        budget_str = str(lead.get('budget', '0')).lower().replace('$', '').replace(' ', '')
        if 'mil' in budget_str:
            budget_str = budget_str.replace('mil', '').strip()
            budget = int(float(budget_str.replace(',', '.')) * 1000)
        else:
            budget_str = budget_str.replace('.', '').replace(',', '')
            budget = int(budget_str)
        timeline_str = str(lead.get('timeline', '99')).lower()
        timeline_str = timeline_str.replace('meses', '').replace('mes', '').strip()
        timeline = int(timeline_str)
    except ValueError:
        return 'COLD'
    if budget >= 80000 and timeline <= 2:
        return 'HOT'
    elif budget >= 40000 and timeline <= 6:
        return 'WARM'
    else:
        return 'COLD'

# ======================================================
# EMAIL
# ======================================================
def send_email(lead):
    try:
        score = lead.get('score', 'COLD')
        sender = 'fbarrenecheam09@gmail.com'
        password = st.secrets['EMAIL_PASSWORD']
        subject = 'Nuevo Lead ' + score + ' - LeadBoost'
        body = 'Nuevo lead en LeadBoost:\n\n'
        body += 'Nombre: ' + str(lead.get('name', '-')) + '\n'
        body += 'Telefono: ' + str(lead.get('phone', '-')) + '\n'
        body += 'Tipo: ' + str(lead.get('property_type', '-')) + '\n'
        body += 'Zona: ' + str(lead.get('area', '-')) + '\n'
        body += 'Presupuesto: $' + str(lead.get('budget', '-')) + '\n'
        body += 'Plazo: ' + str(lead.get('timeline', '-')) + ' meses\n'
        body += 'Score: ' + score + '\n'
        body += 'Fecha: ' + datetime.now().strftime('%Y-%m-%d %H:%M') + '\n'
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = sender
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, sender, msg.as_string())
    except Exception:
        pass

def save_lead(lead):
    try:
        get_supabase().table('leads').insert({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'name': lead.get('name', ''),
            'phone': lead.get('phone', ''),
            'property_type': lead.get('property_type', ''),
            'area': lead.get('area', ''),
            'budget': lead.get('budget', ''),
            'timeline': lead.get('timeline', ''),
            'score': lead.get('score', ''),
        }).execute()
    except Exception as e:
        st.error('Error: ' + str(e))

def get_ai_response(messages):
    try:
        claude = get_claude()
        r = claude.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        return r.content[0].text
    except Exception as e:
        return 'Error: ' + str(e)

def extract_lead(response_text):
    if 'LEAD_COMPLETO:' in response_text:
        try:
            return json.loads(response_text.split('LEAD_COMPLETO:')[1].strip())
        except:
            return None
    return None

# ======================================================
# FIRST MESSAGE
# ======================================================
if not st.session_state.greeted:
    greeting = 'Hola. Soy LeadBoost, tu asistente inmobiliario. Para ayudarte a encontrar la propiedad ideal, me puedes decir tu nombre y que tipo de propiedad estas buscando?'
    st.session_state.chat_history.append(('bot', greeting))
    st.session_state.messages.append({'role': 'assistant', 'content': greeting})
    st.session_state.greeted = True

# ======================================================
# CHAT HISTORY
# ======================================================
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for sender, msg in st.session_state.chat_history:
    if 'LEAD_COMPLETO:' in msg:
        display_msg = msg.split('LEAD_COMPLETO:')[0].strip()
    else:
        display_msg = msg
    msg_html = display_msg.replace('\n', '<br>')
    if sender == 'bot':
        html = '<div class="label-row">// LEADBOOST</div><div class="bubble-bot">' + msg_html + '</div>'
    else:
        html = '<div class="label-row label-user">YOU //</div><div class="bubble-user">' + msg_html + '</div>'
    st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# INPUT
# ======================================================
if not st.session_state.done:
    user_input = st.text_input('MESSAGE', key='input_' + str(len(st.session_state.messages)), label_visibility='collapsed', placeholder='Escribe tu mensaje...')
    if st.button('SEND  //'):
        if user_input.strip():
            st.session_state.chat_history.append(('user', user_input.strip()))
            st.session_state.messages.append({'role': 'user', 'content': user_input.strip()})
            ai_response = get_ai_response(st.session_state.messages)
            st.session_state.chat_history.append(('bot', ai_response))
            st.session_state.messages.append({'role': 'assistant', 'content': ai_response})
            lead = extract_lead(ai_response)
            if lead:
                score = score_lead(lead)
                lead['score'] = score
                save_lead(lead)
                send_email(lead)
                st.session_state.done = True
            st.rerun()

if st.session_state.done:
    if st.button('// NEW CONVERSATION'):
        for key in ['chat_history', 'messages', 'done', 'greeted']:
            del st.session_state[key]
        st.rerun()
