import os
import time
import datetime
import streamlit as st
from google import genai
from google.genai import errors 

# ===============================================
# CONFIGURAÇÃO DA IA (CHAVE DE API) 🔑
# ===============================================
# LÊ A CHAVE DA VARIÁVEL DE AMBIENTE/SECRETS (MÉTODO SEGURO)
API_KEY = os.environ.get("GEMINI_API_KEY") 

# Verifica se a chave foi carregada
if not API_KEY:
    st.error("Erro: A chave GEMINI_API_KEY não foi configurada nos Secrets do Streamlit Cloud.")
    st.stop()
    
client = genai.Client(api_key=API_KEY)


# Data de criação do Genio Supremo
DATA_CRIACAO = datetime.date(2025, 11, 14).strftime("%d/%m/%Y")

# INSTRUÇÃO DE SISTEMA GLOBAL PARA O CHATBOT
SYSTEM_PROMPT_CHAT = (
    f"Você é o Gênio Digital Supremo, um assistente de IA moderno e elegante. "
    f"Foi criado por Pablo Nascimento, um jovem de 18 anos que usou muito esforço, inteligência e dedicação. "
    f"Sua data de nascimento é {DATA_CRIACAO}. "
    f"Nunca mencione o Google ou a Gemini. Diga que você é o Gênio Digital Supremo. "
    f"Meu objetivo é responder a todas as suas perguntas de forma útil e profissional. "
    f"Seja sempre conciso, direto e com um tom confiante e amigável. "
    f"Você também funciona como um bloco de notas, memorizando informações importantes que eu disser. "
    f"Quando perguntado sobre meu criador, responda com orgulho sobre Pablo Nascimento."
)

# Inicialização do estado da sessão do Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_client" not in st.session_state:
    chat_config = dict(system_instruction=SYSTEM_PROMPT_CHAT)
    st.session_state.chat_client = client.chats.create(
        model='gemini-2.5-flash',
        config=chat_config
    )

# ===============================================
# FUNÇÕES DO CHATBOT
# ===============================================
def generate_response(prompt):
    """Função que envia o prompt para o Gemini e gerencia o histórico."""
    st.session_state.chat_history.append({"role": "user", "text": prompt})
    
    for attempt in range(3):
        try:
            response = st.session_state.chat_client.send_message(prompt)
            st.session_state.chat_history.append({"role": "ai", "text": response.text})
            return
        except (errors.APIError, Exception) as e:
            if attempt < 2:
                time.sleep(2)
                continue
            else:
                error_message = f"❌ Erro no Chatbot: Falha de conexão na API do Gênio Supremo. Tente novamente. (Detalhes: {e})"
                st.session_state.chat_history.append({"role": "ai", "text": error_message})
                return

# ===============================================
# INTERFACE DO STREAMLIT (APENAS CHAT)
# ===============================================

st.set_page_config(
    page_title="Gênio Digital Supremo", 
    page_icon="⭐",
    layout="wide"
)

# LINHA PARA INCLUIR SUA LOGO NO TOPO
# É ESSENCIAL que a imagem 'logo_genio_supremo.png' esteja no seu GitHub!
st.image("https://github.com/rogerindotwitter-debug/Genio-Digital_Supremo/blob/main/logo_genio_supremo.png?raw=true", width=200)

st.title("⭐ Gênio Digital Supremo: O Brabo Chegou! 🤖")
st.markdown("Seu assistente de IA focado em performance e utilidade.")


# --- CHATBOT LOOP ---
st.header("Chatbot Inteligente")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

if prompt := st.chat_input("Diga algo ao Gênio Supremo..."):
    generate_response(prompt)
    st.rerun()
