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
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg", 
                    aspect_ratio="1:1"
                )
            )
            
            if not response.generated_images:
                return "❌ A API não retornou nenhuma imagem para este prompt. Tente outro."
            
            return response.generated_images[0].image
            
        except (errors.APIError, Exception) as e:
            if attempt < 2:
                time.sleep(2)
                continue
            else:
                return f"❌ Erro ao gerar imagem: Falha na conexão ou restrição na chave de API para imagens. (Detalhes: {e})"

# ===============================================
# INTERFACE DO STREAMLIT
# ===============================================

# CORREÇÃO FINAL APLICADA: Configuração da página simplificada
st.set_page_config(
    page_title="Gênio Digital Supremo", 
    page_icon="⭐"
)

st.title("⭐ Gênio Digital Supremo: O Brabo Chegou! 🤖🎨")
st.markdown("Seu assistente de IA profissional com capacidade de Chat e Geração de Imagens.")

# Cria as abas
tab_chat, tab_image = st.tabs(["💬 Chatbot", "🖼️ Gerador de Imagens"])

# --- CHATBOT TAB ---
with tab_chat:
    st.header("Chatbot Inteligente")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    if prompt := st.chat_input("Diga algo ao Gênio Supremo..."):
        generate_response(prompt)
        st.experimental_rerun()


# --- IMAGEM TAB ---
with tab_image:
    st.header("Gerador de Arte Digital")
    
    image_prompt = st.text_area(
        "Descrição da Imagem (em inglês para melhores resultados):",
        placeholder="Ex: 'A futuristic car flying through a neon city, cinematic'",
        height=100
    )
    
    if st.button("Gerar Imagem", type="primary"):
        with st.spinner("Gerando sua obra de arte..."):
            image_result = generate_image(image_prompt)
            
            if isinstance(image_result, str):
                st.error(image_result)
            elif image_result is not None:
                st.image(image_result, caption=image_prompt, use_column_width=True)
