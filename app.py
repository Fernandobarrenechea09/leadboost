import streamlit as st
from supabase import create_client
from datetime import datetime
import anthropic
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# —————————————————–

# PAGE CONFIG

# —————————————————–

st.set_page_config(
page_title=“LEADBOOST”,
page_icon=”#”,
layout=“centered”
)

# —————————————————–

# THEME STATE

# —————————————————–

if “theme” not in st.session_state:
st.session_state.theme = “light”

# —————————————————–

# THEME TOGGLE

# —————————————————–

col_spacer, col_toggle = st.columns([5, 1])
with col_toggle:
icon = “Dark” if st.session_state.theme == “light” else “Light”
if st.button(icon, key=“theme_toggle”):
st.session_state.theme = “dark” if st.session_state.theme == “light” else “light”
st.rerun()

# —————————————————–

# THEME COLORS

# —————————————————–

if st.session_state.theme == “light”:
BG = “#F5F1E8”
PANEL = “#FFFFFF”
BORDER = “#D4CFC0”
TEXT = “#1A1A1A”
TEXT_DIM = “#6B6B6B”
ACCENT = “#1A1A1A”
BUBBLE_BOT = “#FAF7EE”
BUBBLE_USR = “#1A1A1A”
BUBBLE_USR_TXT = “#F5F1E8”
else:
BG = “#0F0F0F”
PANEL = “#1A1A1A”
BORDER = “#2A2A2A”
TEXT = “#F0F0F0”
TEXT_DIM = “#8A8A8A”
ACCENT = “#F0F0F0”
BUBBLE_BOT = “#1A1A1A”
BUBBLE_USR = “#F0F0F0”
BUBBLE_USR_TXT = “#0F0F0F”

# —————————————————–

# CUSTOM CSS

# —————————————————–

css = “””

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp, .main {
    font-family: 'Inter', sans-serif;
    background-color: BG_COLOR !important;
    color: TEXT_COLOR !important;
}
.stApp { background-color: BG_COLOR !important; }

.lb-header {
    border: 1px solid BORDER_COLOR;
    background: PANEL_COLOR;
    border-radius: 4px;
    padding: 14px 20px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.lb-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: TEXT_DIM_COLOR;
    text-transform: uppercase;
}
.lb-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: TEXT_COLOR;
    line-height: 1;
    margin: 4px 0 0 0;
    font-style: italic;
}
.lb-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.1em;
    text-align: right;
}

.chat-wrap { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }

.bubble-bot {
    background: BUBBLE_BOT_COLOR;
    border: 1px solid BORDER_COLOR;
    border-radius: 2px 14px 14px 14px;
    padding: 12px 16px;
    max-width: 85%;
    align-self: flex-start;
    font-size: 0.92rem;
    line-height: 1.55;
    color: TEXT_COLOR;
}
.bubble-user {
    background: BUBBLE_USR_COLOR;
    color: BUBBLE_USR_TXT_COLOR;
    border-radius: 14px 14px 2px 14px;
    padding: 12px 16px;
    max-width: 85%;
    align-self: flex-end;
    font-size: 0.92rem;
    line-height: 1.55;
}
.label-row {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: TEXT_DIM_COLOR;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.label-user { text-align: right; }

.stTextInput > div > div > input {
    background: PANEL_COLOR !important;
    color: TEXT_COLOR !important;
    border: 1px solid BORDER_COLOR !important;
    border-radius: 2px !important;
    padding: 11px 14px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
}
.stTextInput label {
    color: TEXT_DIM_COLOR !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

div.stButton > button {
    background: ACCENT_COLOR;
    color: BG_COLOR;
    border: none;
    border-radius: 2px;
    padding: 10px 24px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    cursor: pointer;
}
div.stButton > button:hover { opacity: 0.82; }

header { visibility: hidden; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>

“””

css = css.replace(“BG_COLOR”, BG)
css = css.replace(“PANEL_COLOR”, PANEL)
css = css.replace(“BORDER_COLOR”, BORDER)
css = css.replace(“TEXT_DIM_COLOR”, TEXT_DIM)
css = css.replace(“TEXT_COLOR”, TEXT)
css = css.replace(“ACCENT_COLOR”, ACCENT)
css = css.replace(“BUBBLE_BOT_COLOR”, BUBBLE_BOT)
css = css.replace(“BUBBLE_USR_COLOR”, BUBBLE_USR)
css = css.replace(“BUBBLE_USR_TXT_COLOR”, BUBBLE_USR_TXT)

st.markdown(css, unsafe_allow_html=True)

# —————————————————–

# CONNECTIONS

# —————————————————–

@st.cache_resource
def get_supabase():
return create_client(st.secrets[“SUPABASE_URL”], st.secrets[“SUPABASE_KEY”])

@st.cache_resource
def get_claude():
return anthropic.Anthropic(api_key=st.secrets[“ANTHROPIC_KEY”])

# —————————————————–

# SYSTEM PROMPT

# —————————————————–

SYSTEM_PROMPT = “”“Eres LeadBoost, un asistente inmobiliario virtual para agencias de bienes raices en Bolivia. Tu trabajo es recopilar exactamente 6 datos del usuario mediante una conversacion natural en espanol.

Los 6 datos que necesitas son:

1. Nombre completo
1. Tipo de propiedad (Casa, Departamento, Terreno, Local comercial)
1. Zona o barrio de preferencia
1. Presupuesto aproximado en dolares (solo el numero, ejemplo: 150000)
1. Plazo en meses para comprar o rentar (solo el numero, ejemplo: 2)
1. Numero de telefono

EL PROCESO TIENE 3 FASES:

FASE 1 - RECOPILACION:

- Conversa de forma natural y amigable
- Si el usuario da multiple informacion en un mensaje, extraela toda
- Solo pregunta por los datos que faltan

FASE 2 - CONFIRMACION:
Cuando tengas los 6 datos muestra este resumen:

Perfecto, antes de finalizar dejame confirmar tu informacion:

Nombre: [nombre]
Tipo de propiedad: [tipo]
Zona: [zona]
Presupuesto: [presupuesto]
Plazo: [plazo] meses
Telefono: [telefono]

Es correcta toda esta informacion?

FASE 3 - CIERRE:
Cuando el usuario confirme responde EXACTAMENTE asi:

Gracias [nombre]! Hemos registrado tu informacion correctamente. En breve uno de nuestros agentes se pondra en contacto contigo.
LEAD_COMPLETO:{“name”:”…”,“property_type”:”…”,“area”:”…”,“budget”:“150000”,“timeline”:“2”,“phone”:”…”}

IMPORTANTE: En el JSON budget y timeline deben ser solo numeros sin texto.”””

# —————————————————–

# SESSION STATE

# —————————————————–

if “chat_history” not in st.session_state: st.session_state.chat_history = []
if “messages” not in st.session_state: st.session_state.messages = []
if “done” not in st.session_state: st.session_state.done = False
if “greeted” not in st.session_state: st.session_state.greeted = False

# —————————————————–

# SCORING

# —————————————————–

def score_lead(lead):
try:
budget_str = str(lead.get(“budget”, “0”)).lower().replace(”$”, “”).replace(” “, “”)
if “mil” in budget_str:
budget_str = budget_str.replace(“mil”, “”).strip()
budget = int(float(budget_str.replace(”,”, “.”)) * 1000)
else:
budget_str = budget_str.replace(”.”, “”).replace(”,”, “”)
budget = int(budget_str)
timeline_str = str(lead.get(“timeline”, “99”)).lower()
timeline_str = timeline_str.replace(“meses”, “”).replace(“mes”, “”).strip()
timeline = int(timeline_str)
except ValueError:
return “COLD”
if budget >= 80000 and timeline <= 2:
return “HOT”
elif budget >= 40000 and timeline <= 6:
return “WARM”
else:
return “COLD”

# —————————————————–

# EMAIL

# —————————————————–

def send_email(lead):
try:
score = lead.get(“score”, “COLD”)
sender = “fbarrenecheam09@gmail.com”
receiver = “fbarrenecheam09@gmail.com”
password = st.secrets[“EMAIL_PASSWORD”]
subject = “Nuevo Lead “ + score + “ - LeadBoost”
body = “Nuevo lead registrado en LeadBoost:\n\n”
body += “Nombre: “ + str(lead.get(‘name’, ‘-’)) + “\n”
body += “Telefono: “ + str(lead.get(‘phone’, ‘-’)) + “\n”
body += “Tipo propiedad: “ + str(lead.get(‘property_type’, ‘-’)) + “\n”
body += “Zona: “ + str(lead.get(‘area’, ‘-’)) + “\n”
body += “Presupuesto: $” + str(lead.get(‘budget’, ‘-’)) + “\n”
body += “Plazo: “ + str(lead.get(‘timeline’, ‘-’)) + “ meses\n”
body += “Clasificacion: “ + score + “\n”
body += “Fecha: “ + datetime.now().strftime(’%Y-%m-%d %H:%M’) + “\n\n”
body += “– LeadBoost, Bolivia”
msg = MIMEMultipart()
msg[“From”] = sender
msg[“To”] = receiver
msg[“Subject”] = subject
msg.attach(MIMEText(body, “plain”))
with smtplib.SMTP_SSL(“smtp.gmail.com”, 465) as server:
server.login(sender, password)
server.sendmail(sender, receiver, msg.as_string())
except Exception:
pass

# —————————————————–

# SAVE LEAD

# —————————————————–

def save_lead(lead):
try:
supabase = get_supabase()
supabase.table(“leads”).insert({
“timestamp”: datetime.now().strftime(”%Y-%m-%d %H:%M”),
“name”: lead.get(“name”, “”),
“phone”: lead.get(“phone”, “”),
“property_type”: lead.get(“property_type”, “”),
“area”: lead.get(“area”, “”),
“budget”: lead.get(“budget”, “”),
“timeline”: lead.get(“timeline”, “”),
“score”: lead.get(“score”, “”),
}).execute()
except Exception as e:
st.error(“Error: “ + str(e))

# —————————————————–

# AI RESPONSE

# —————————————————–

def get_ai_response(messages):
try:
claude = get_claude()
response = claude.messages.create(
model=“claude-haiku-4-5-20251001”,
max_tokens=1000,
system=SYSTEM_PROMPT,
messages=messages
)
return response.content[0].text
except Exception as e:
return “Error: “ + str(e)

def extract_lead(response_text):
if “LEAD_COMPLETO:” in response_text:
try:
json_str = response_text.split(“LEAD_COMPLETO:”)[1].strip()
return json.loads(json_str)
except:
return None
return None

# —————————————————–

# HEADER

# —————————————————–

now_time = datetime.now().strftime(”%H:%M”)
today = datetime.now().strftime(”%A, %B %d, %Y”).upper()

header_html = ‘<div class="lb-header">’
header_html += ‘<div>’
header_html += ‘<div class="lb-label">LEADBOOST // V3.0</div>’
header_html += ‘<div class="lb-title">Good day.</div>’
header_html += ‘</div>’
header_html += ‘<div class="lb-sub">’ + today + ’<br>BOLIVIA - ’ + now_time + ‘</div>’
header_html += ‘</div>’
st.markdown(header_html, unsafe_allow_html=True)

# —————————————————–

# FIRST MESSAGE

# —————————————————–

if not st.session_state.greeted:
greeting = “Hola. Soy LeadBoost, tu asistente inmobiliario. Para ayudarte a encontrar la propiedad ideal, me puedes decir tu nombre y que tipo de propiedad estas buscando?”
st.session_state.chat_history.append((“bot”, greeting))
st.session_state.messages.append({“role”: “assistant”, “content”: greeting})
st.session_state.greeted = True

# —————————————————–

# CHAT HISTORY

# —————————————————–

st.markdown(’<div class="chat-wrap">’, unsafe_allow_html=True)
for sender, msg in st.session_state.chat_history:
if “LEAD_COMPLETO:” in msg:
display_msg = msg.split(“LEAD_COMPLETO:”)[0].strip()
else:
display_msg = msg
msg_html = display_msg.replace(”\n”, “<br>”)
if sender == “bot”:
html = ‘<div class="label-row">// LEADBOOST</div><div class="bubble-bot">’ + msg_html + ‘</div>’
else:
html = ‘<div class="label-row label-user">YOU //</div><div class="bubble-user">’ + msg_html + ‘</div>’
st.markdown(html, unsafe_allow_html=True)
st.markdown(’</div>’, unsafe_allow_html=True)

# —————————————————–

# INPUT

# —————————————————–

if not st.session_state.done:
user_input = st.text_input(“MESSAGE”, key=“input_” + str(len(st.session_state.messages)), label_visibility=“collapsed”, placeholder=“Escribe tu mensaje…”)

```
if st.button("SEND"):
    if user_input.strip():
        st.session_state.chat_history.append(("user", user_input.strip()))
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        ai_response = get_ai_response(st.session_state.messages)
        st.session_state.chat_history.append(("bot", ai_response))
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        lead = extract_lead(ai_response)
        if lead:
            score = score_lead(lead)
            lead["score"] = score
            save_lead(lead)
            send_email(lead)
            st.session_state.done = True
        st.rerun()
```

if st.session_state.done:
if st.button(“NEW CONVERSATION”):
for key in [“chat_history”, “messages”, “done”, “greeted”]:
del st.session_state[key]
st.rerun()
