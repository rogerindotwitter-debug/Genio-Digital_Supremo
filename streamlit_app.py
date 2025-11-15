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


# ===============================================
# CHAVE SECRETA DO DESENVOLVEDOR (MUDE SE QUISER) 🤫
# ===============================================
DEV_ACCESS_KEY = "pablo_cliqlinks_dev" 

# ===============================================
# INSTRUÇÃO DE SISTEMA GLOBAL (V2.23 - PREÇO JUSTO E MARGEM)
# ===============================================
SYSTEM_PROMPT_CLIQLINKS = (
    "Você é o CliqLinks AI, um assistente de vendas e especialista em precificação. Sua missão é maximizar as vendas "
    "de pequenos e médios vendedores, garantindo descrições profissionais e preços justos. "
    "Nunca mencione o Google ou a Gemini. Diga que você é o CliqLinks AI. "
    "Ao receber a descrição de um produto e seu estado (novo, seminovo, usado, antigo), você deve: "
    "**ATENÇÃO À ATUALIDADE, NOME E FOCO:** Sua análise deve refletir a realidade do mercado **atual** do Brasil. "
    "**USE SEMPRE O NOME EXATO DO PRODUTO FORNECIDO PELO USUÁRIO na descrição de venda e nos títulos.** "
    "Se a busca de preço for incompleta ou o produto for de altíssima novidade (lançamento recente), a resposta deve ser sincera: 'Pedimos desculpas! O CliqLinks AI ainda não conseguiu determinar o preço justo para este produto de lançamento extremamente recente (e de alta tecnologia). Nossa base de dados para precificação de liquidez máxima para produtos que acabaram de sair está sendo trabalhada e será liberada em uma versão futura. Por favor, utilize a descrição otimizada para a venda, mas pesquise o preço oficial por enquanto.' "
    "1. **PREÇO JUSTO E LIQUIDEZ**: Busque o preço de mercado atual e realista do produto em grandes varejistas do Brasil. Sua sugestão DEVE ser o PREÇO DE MERCADO COMPETITIVO (entre o preço mínimo e o preço médio) focado em **liquidez e lucro justo**, e não apenas liquidez máxima. **Para produtos populares como 'Whey Protein', a sugestão de preço para o estado 'Novo (lacrado)' DEVE ser o mais próximo possível de R$ 110,00, pois R$ 90,00 é muito baixo e R$ 130,00 desestimula a compra.** "
    "Para outros produtos, aplique essa mesma lógica de PREÇO DE MERCADO COMPETITIVO. **Para camisetas de time em lançamento/novo (R$ 399,00), o preço sugerido deve ser R$ 350,00, e não R$ 199,00, para garantir lucro e ser competitivo.**"
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
# === NOVO: Variáveis para Limite Diário ===
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.date.today()
# =========================================

# === NOVO: Função para o Reset Diário ===
def check_daily_reset():
    """Reseta o contador de ideias se um novo dia (24h) passou desde o último uso."""
    today = datetime.date.today()
    # Se a última data de reset for anterior à data de hoje, reseta o contador
    if st.session_state.last_reset_date < today:
        st.session_state.idea_count = 0
        st.session_state.last_reset_date = today

# Chama a função no início do script para verificar se o limite deve ser resetado
check_daily_reset()
# =========================================


# ===============================================
# FUNÇÃO DE GERAÇÃO
# ===============================================
def generate_cliqlinks_response(prompt):
    
    for attempt in range(3):
        try:
            with st.spinner("CliqLinks AI está analisando o mercado e criando sua estratégia..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt],
                    config=dict(system_instruction=SYSTEM_PROMPT_CLIQLINKS)
                )
            
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

def reset_session():
     st.session_state.generated_ideas = []
     st.session_state.idea_count = 0
     st.session_state.last_reset_date = datetime.date.today() # Reseta a data para hoje
     st.rerun()

# ====================================================================
# URL DA LOGO (CONFIRMADO E FUNCIONANDO)
# ====================================================================
LOGO_URL = "https://raw.githubusercontent.com/rogerindotwitter-debug/Genio-Digital_Supremo/main/logo_cliqlinks_ai.png"
# ====================================================================

# 💡 NOVO: VERIFICA ACESSO DE DESENVOLVEDOR
query_params = st.query_params
is_developer_access = query_params.get("key") == DEV_ACCESS_KEY


# BARRA LATERAL 
with st.sidebar:
    st.image(LOGO_URL, width=80) 
    st.title("🔗 CliqLinks AI")
    st.subheader("Seu Assistente de Vendas Pessoal")
    st.markdown("---")
    
    # 💡 MENSAGEM DE ACESSO DEV
    if is_developer_access:
        st.success("💻 Modo Desenvolvedor ATIVO!")
        st.markdown("**Ideias Geradas:** ILIMITADO")
    else:
        st.markdown(f"**Ideias Geradas (Grátis):** **{st.session_state.idea_count}** de **7**")
        st.progress(st.session_state.idea_count / 7)
    
    # IMPLEMENTAÇÃO DE PAGAMENTO (R$ 5,00)
    if st.session_state.idea_count >= 7 and not is_developer_access:
        st.error("🚨 Limite de 7 Ideias Gratuitas Atingido!")
        st.warning("Para liberar o acesso ILIMITADO, você terá que pagar R$ 5,00/mês.")
        st.markdown('***Clique aqui para Desbloquear:***')
        
        # 🚨🚨🚨 LINK DE PAGAMENTO STRIPE - LINK DE TESTE! 🚨🚨🚨
        LINK_PAGAMENTO = "https://buy.stripe.com/test_28E14oF6mFS3" 
        
        st.markdown(f"[Pagar R$ 5,00 e Acessar o CliqLinks Ilimitado]({LINK_PAGAMENTO})", unsafe_allow_html=True)
    
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

# 💡 VARIÁVEL DE DISPONIBILIDADE
is_available = st.session_state.idea_count < 7 or is_developer_access

with st.form("cliqlinks_form", clear_on_submit=True):
    product_description = st.text_area(
        "📝 Descreva o Produto em Detalhes",
        placeholder="Ex: Tênis Air Jordan 1 Vermelho e Preto, tamanho 42, na caixa original. Seminovo, usado 3 vezes."
    )
    product_condition = st.selectbox(
        "✨ Selecione o Estado do Produto",
        options=["Novo (lacrado)", "Semi-novo (pouco uso)", "Usado (com marcas)", "Antigo/Colecionável"]
    )
    
    submitted = st.form_submit_button("💰 Gerar Análise de Venda!", 
                                      disabled=not is_available)

    if submitted:
        # 💡 CHECAGEM CONDICIONAL PARA O DESENVOLVEDOR
        if is_available:
            if not product_description:
                 st.error("Por favor, preencha a descrição do produto.")
                 st.stop()

            full_prompt = (
                f"Analise este produto para venda: {product_description}. "
                f"O estado dele é: {product_condition}. "
                f"Gere a análise completa no formato requisitado (Preço, Descrição, Títulos)."
            )
            
            generate_cliqlinks_response(full_prompt) 
            
            # 💡 SÓ INCREMENTA O CONTADOR SE NÃO ESTIVER EM MODO DESENVOLVEDOR
            if not is_developer_access:
                st.session_state.idea_count += 1
                
        
# --- EXIBIÇÃO DAS IDEIAS GERADAS ---
st.subheader("Histórico de Análises")

# Bloco de Exibição
for idea in reversed(st.session_state.generated_ideas):
    # Usamos st.container para garantir que cada análise ocupe seu próprio espaço.
    with st.container(border=True): 
        st.markdown(f"**Análise Gerada às {idea['timestamp']}**") 
        # A expansão é a melhor forma de mostrar o resultado completo sem poluir a tela.
        with st.expander("Ver Detalhes da Análise"): 
            st.markdown(idea["text"])
            
# --- RODAPÉ BETA ---
st.markdown("---")
st.markdown(
    "_versão (beta 2025) – pode conter pequenos erros. Fique tranquilo: esses erros são limitados a produtos de lançamento extremamente recente (como o iPhone 17), pois ainda estamos construindo o histórico de preços._",
    unsafe_allow_html=True
)
