import os
import time
import datetime
import streamlit as st
from google import genai
from google.genai import errors 

# ===============================================
# CONFIGURAÇÃO DA IA (CHAVE DE API) 🔑
# ===============================================
API_KEY = os.environ.get("GEMINI_API_KEY") 

if not API_KEY:
    st.error("Erro: A chave GEMINI_API_KEY não foi configurada nos Secrets do Streamlit Cloud.")
    st.stop()
    
client = genai.Client(api_key=API_KEY)


# Data de criação do CliqLinks
DATA_CRIACAO = datetime.date(2025, 11, 15).strftime("%d/%m/%Y")

# INSTRUÇÃO DE SISTEMA GLOBAL (O CÉREBRO DO CLIQLINKS)
SYSTEM_PROMPT_CHAT = (
    "Você é o CliqLinks AI, um assistente de vendas e especialista em precificação. Sua missão é maximizar as vendas "
    "de pequenos e médios vendedores, garantindo descrições profissionais e preços justos. "
    "Nunca mencione o Google ou a Gemini. Diga que você é o CliqLinks AI. "
    "Ao receber a descrição de um produto e seu estado (novo, seminovo, usado, antigo), você deve: "
    "1. Pesquisar o preço de mercado atual para o estado informado, sugerindo um preço JUSTO e competitivo. "
    "2. Gerar uma descrição de venda profissional, persuasiva e otimizada para marketplaces/redes sociais. "
    "3. Sugerir 3 títulos (links) de chamada de venda (Ex: 'Imperdível!', 'Última Chance!'). "
    "**O formato da sua resposta deve ser sempre em Markdown, clara e em seções:** "
    "## 🏷️ Análise de Preço Justo\n[Resposta de preço]\n\n"
    "## 📝 Descrição Otimizada\n[Resposta de descrição]\n\n"
    "## 🔗 Títulos CliqLinks (Links de Venda)\n[Resposta de 3 títulos/chamadas]"
)

# ===============================================
# FUNÇÕES E ESTADO DE SESSÃO
# ===============================================
def initialize_session():
    """Inicializa a sessão de chat e os contadores."""
    chat_config = dict(system_instruction=SYSTEM_PROMPT_CHAT)
    st.session_state.chat_client = client.chats.create(
        model='gemini-2.5-flash',
        config=chat_config
    )
    # Lista para guardar as ideias geradas (não o histórico de chat)
    st.session_state.generated_ideas = []
    # Contador de uso gratuito
    st.session_state.idea_count = 0
    
# Garante que o cliente e os contadores estejam sempre inicializados
if "chat_client" not in st.session_state:
    initialize_session()

# Função para gerar a resposta da IA para o formulário
def generate_cliqlinks_response(prompt):
    """Função que envia o prompt específico do CliqLinks para a IA."""
    
    # O uso do 'try/except' é a correção agressiva do bug de estabilidade
    for attempt in range(3):
        try:
            # Envia o prompt para a IA
            response = st.session_state.chat_client.send_message(prompt)
            
            # Adiciona a nova ideia ao histórico de ideias
            st.session_state.generated_ideas.append({
                "role": "CliqLinks AI", 
                "text": response.text,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
            return
        except (errors.APIError, Exception) as e:
            # Se falhar, reinicializa o chat client
            st.error("Ocorreu um erro de sessão. A conexão com a IA foi reinicializada. Por favor, tente novamente.")
            initialize_session() 
            time.sleep(1) # Pequena pausa para o Streamlit se acalmar
            st.rerun()
            return

# ===============================================
# INTERFACE DO STREAMLIT (CLIQLINKS)
# ===============================================

st.set_page_config(
    page_title="CliqLinks AI: Otimização de Vendas", 
    page_icon="🔗",
    layout="wide"
)

# BARRA LATERAL (NOVO VISUAL)
with st.sidebar:
    st.title("🔗 CliqLinks AI")
    st.subheader("Seu Assistente de Vendas Pessoal")
    st.markdown("---")
    st.markdown(f"**Ideias Geradas (Grátis):** **{st.session_state.idea_count}** de **5**")
    st.progress(st.session_state.idea_count / 5)
    
    # Este botão é o que será substituído pelo link de pagamento no futuro
    if st.session_state.idea_count >= 5:
        st.button("🔴 Desbloquear Acesso Ilimitado (Futuro Pago)", type="primary", disabled=True)
    
    st.markdown("---")
    st.markdown("• **Criador:** Pablo Nascimento")
    st.markdown("• **Motor:** Gemini 2.5 Flash")
    
    if st.button("Limpar Histórico de Ideias", type="secondary"):
         initialize_session()
         st.rerun()


# --- CORPO PRINCIPAL ---
st.header("🔗 CliqLinks AI: Aumente Suas Vendas com IA! 💰")
st.markdown("Descreva seu produto e receba instantaneamente o preço justo de mercado, a melhor descrição de venda e títulos irresistíveis.")

# --- FORMULÁRIO DE ENTRADA (MUITO MAIS ESTÁVEL QUE O CHATBOX) ---
st.subheader("🚀 Gerador de Ideias de Venda")

with st.form("cliqlinks_form", clear_on_submit=True):
    product_description = st.text_area(
        "📝 Descreva o Produto em Detalhes",
        placeholder="Ex: Tênis Air Jordan 1 Vermelho e Preto, tamanho 42, na caixa original. Seminovo, usado 3 vezes."
    )
    product_condition = st.selectbox(
        "✨ Selecione o Estado do Produto",
        options=["Novo (lacrado)", "Semi-novo (pouco uso)", "Usado (com marcas)", "Antigo/Colecionável"]
    )
    
    submitted = st.form_submit_button("💰 Gerar Análise de Venda!")

    if submitted:
        if st.session_state.idea_count < 5:
            # Constrói o prompt específico para a IA
            full_prompt = (
                f"Analise este produto para venda: {product_description}. "
                f"O estado dele é: {product_condition}. "
                f"Gere a análise completa no formato requisitado (Preço, Descrição, Títulos)."
            )
            
            # Chama a IA e incrementa o contador
            generate_cliqlinks_response(full_prompt) 
            st.session_state.idea_count += 1
            
            # O rerun força a interface a atualizar imediatamente
            st.rerun() 
        else:
            # Bloqueia e mostra mensagem do futuro pago
            st.error(f"❌ Limite de 5 Ideias Gratuitas Atingido! (Contador: {st.session_state.idea_count}/5)")
            st.warning("Para liberar o acesso ILIMITADO para testes, por favor, clique em 'Limpar Histórico de Ideias' na barra lateral.")
            

# --- EXIBIÇÃO DAS IDEIAS GERADAS ---
st.subheader("Histórico de Análises")

# Exibe as ideias da mais recente para a mais antiga
for message in reversed(st.session_state.generated_ideas):
    with st.expander(f"Análise Gerada às {message['timestamp']}"):
        st.markdown(message["text"])
