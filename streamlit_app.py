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
    
# Inicializa o cliente da API
client = genai.Client(api_key=API_KEY)


# INSTRUÇÃO DE SISTEMA GLOBAL (O CÉREBRO DO CLIQLINKS)
SYSTEM_PROMPT_CLIQLINKS = (
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

# Inicializa o estado de sessão
if "generated_ideas" not in st.session_state:
    st.session_state.generated_ideas = []
if "idea_count" not in st.session_state:
    st.session_state.idea_count = 0

# ===============================================
# FUNÇÃO DE GERAÇÃO (MAIS ESTÁVEL)
# ===============================================
def generate_cliqlinks_response(prompt):
    """Função que envia o prompt diretamente para o modelo (Sem chat, alta estabilidade)."""
    
    # O uso do 'try/except' é a correção agressiva do bug de estabilidade
    for attempt in range(3):
        try:
            with st.spinner("CliqLinks AI está analisando o mercado e criando sua estratégia..."):
                # Chama a API de forma direta e sem manter um histórico de chat
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt],
                    config=dict(system_instruction=SYSTEM_PROMPT_CLIQLINKS)
                )
            
            # Adiciona a nova ideia ao histórico de ideias
            st.session_state.generated_ideas.append({
                "role": "CliqLinks AI", 
                "text": response.text,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
            return
        except (errors.APIError, Exception) as e:
            st.error(f"Ocorreu um erro de conexão/API. Por favor, tente novamente. Detalhes: {e}")
            time.sleep(1)
            return

# ===============================================
# INTERFACE DO STREAMLIT (CLIQLINKS)
# ===============================================

st.set_page_config(
    page_title="CliqLinks AI: Otimização de Vendas", 
    page_icon="🔗",
    layout="wide"
)

# FUNÇÃO PARA RESETAR A SESSÃO
def reset_session():
     st.session_state.generated_ideas = []
     st.session_state.idea_count = 0
     st.rerun()

# ====================================================================
# *** LOGO DO CLIQLINKS AI ***
# ====================================================================
# ATENÇÃO: SUBSTITUA A URL ABAIXO pela URL da sua logo no GitHub.
# Certifique-se de que a logo foi otimizada para menos de 1MB!
LOGO_URL = "https://github.com/rogerindotwitter-debug/Genio-Digital_Supremo/blob/main/logo_cliqlinks_ai.png?raw=true"
# Recomenda-se width=250.
st.image(LOGO_URL, width=250)
# ====================================================================


# BARRA LATERAL (VISUAL MODERNO E CONFORME O TEMA)
with st.sidebar:
    st.title("🔗 CliqLinks AI")
    st.subheader("Seu Assistente de Vendas Pessoal")
    st.markdown("---")
    st.markdown(f"**Ideias Geradas (Grátis):** **{st.session_state.idea_count}** de **5**")
    st.progress(st.session_state.idea_count / 5)
    
    # FUTURA IMPLEMENTAÇÃO DE PAGAMENTO (R$ 5,00)
    if st.session_state.idea_count >= 5:
        st.error("🚨 Limite de 5 Ideias Gratuitas Atingido!")
        st.warning("Para liberar o acesso ILIMITADO (20 links/dia), você terá que pagar R$ 5,00/mês.")
        # VOCÊ IRÁ SUBSTITUIR ESTE BOTÃO PELO SEU LINK DE PAGAMENTO DO STRIPE!
        st.markdown("[[Pagar e Desbloquear Agora!](LINK_DO_SEU_PAGAMENTO_STRIPE_AQUI)]")
    
    st.markdown("---")
    st.markdown("• **Criador:** Pablo Nascimento")
    st.markdown("• **Motor:** Gemini 2.5 Flash")
    
    if st.button("Limpar Histórico de Ideias", type="secondary"):
         reset_session()


# --- CORPO PRINCIPAL ---
st.header("🔗 CliqLinks AI: Aumente Suas Vendas com IA! 💰")
st.markdown("Descreva seu produto e receba instantaneamente o preço justo de mercado, a melhor descrição de venda e títulos irresistíveis.")

# --- FORMULÁRIO DE ENTRADA ---
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
    
    # O botão só fica ativo se o contador for menor que 5 (ou se for o futuro pago)
    submitted = st.form_submit_button("💰 Gerar Análise de Venda!", 
                                      disabled=st.session_state.idea_count >= 5)

    if submitted:
        if st.session_state.idea_count < 5:
            if not product_description:
                 st.error("Por favor, preencha a descrição do produto.")
                 st.stop()

            # Constrói o prompt específico para a IA
            full_prompt = (
                f"Analise este produto para venda: {product_description}. "
                f"O estado dele é: {product_condition}. "
                f"Gere a análise completa no formato requisitado (Preço, Descrição, Títulos)."
            )
            
            # Chama a IA, incrementa o contador e força a atualização
            generate_cliqlinks_response(full_prompt) 
            st.session_state.idea_count += 1
            st.rerun()
        # O else já é tratado pelo disabled no botão e pelas mensagens acima.
            

# --- EXIBIÇÃO DAS IDEIAS GERADAS ---
st.subheader("Histórico de Análises")

# Exibe as ideias da mais recente para a mais antiga
for idea in reversed(st.session_state.generated_ideas):
    with st.expander(f"Análise Gerada às {idea['timestamp']}"):
        st.markdown(idea["text"])
