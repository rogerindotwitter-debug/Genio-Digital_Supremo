import os
import time
import datetime
import streamlit as st
from google import genai
from google.genai import errors 
from PIL import Image 

# ===============================================
# CONFIGURAÇÃO DA IA (CHAVE DE API) 🔑
# ===============================================
# LÊ A CHAVE DA VARIÁVEL DE AMBIENTE/SECRETS (MÉTODO SEGURO DO STREAMLIT CLOUD)
# A CHAVE DEVE SER CONFIGURADA LÁ COM O NOME "GEMINI_API_KEY"
API_KEY = os.environ.get("GEMINI_API_KEY") 

# Verifica se a chave foi carregada
if not API_KEY:
    st.error("Erro: A chave GEMINI_API_KEY não foi configurada nos Secrets do Streamlit Cloud. Você precisa configurar um 'Secret' chamado 'GEMINI_API_KEY'.")
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
    f"Meu objetivo é responder a todas as suas perguntas de forma útil. "
    f"Eu também funciono como um bloco de notas, memorizando informações importantes que você me disser. "
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
# FUNÇÃO DE GERAÇÃO DE IMAGENS
# ===============================================
def generate_image(prompt: str) -> Image.Image | str:
    """Função que chama a API Imagen para gerar a imagem."""
    if not prompt:
        return "Por favor, digite uma descrição para a imagem."
    
    for attempt in range(3):
        try:
            response = client.models.generate_images(
                model='imagen-3.0
