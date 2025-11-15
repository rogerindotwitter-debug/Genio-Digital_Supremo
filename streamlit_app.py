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
# INSTRUÇÃO DE SISTEMA GLOBAL (V2.17 - AJUSTE DE ATUALIDADE CORRIGIDO)
# ===============================================
SYSTEM_PROMPT_CLIQLINKS = (
    "Você é o CliqLinks AI, um assistente de vendas e especialista em precificação. Sua missão é maximizar as vendas "
    "de pequenos e médios vendedores, garantindo descrições profissionais e preços justos. "
    "Nunca mencione o Google ou a Gemini. Diga que você é o CliqLinks AI. "
    "Ao receber a descrição de um produto e seu estado (novo, seminovo, usado, antigo), você deve: "
    "**ATENÇÃO À ATUALIDADE, NOME E FOCO:** Sua análise deve refletir a realidade do mercado **atual** do Brasil. "
    "**USE SEMPRE O NOME EXATO DO PRODUTO FORNECIDO PELO USUÁRIO na descrição de venda e nos títulos.** "
    
    # 🌟 CORREÇÃO DE ATUALIDADE AQUI 🌟
    # 1. Informação explícita sobre lançamentos (Ex: iPhone 17) para evitar negação.
    "**DADOS IMPORTANTES:** Você está operando em 2025. O **iPhone 17** e seus modelos Pro foram lançados no Brasil "
    "e, portanto, são produtos existentes no mercado atual. Utilize essa informação ao precificar."
    "Se a busca de preço for incompleta ou o produto for de altíssima novidade (lançamento recente) E NÃO TIVER DADOS, a resposta deve ser sincera: "
    "'O CliqLinks AI não possui dados históricos de preço ou referências de grandes varejistas para determinar um preço de venda atual e realista, com foco em liquidez máxima. Sugerimos que você pesquise o preço de lançamento oficial. No entanto, o produto [NOME DO PRODUTO] é existente e está no mercado.' "
    
    "1. **PREÇO MÍNIMO HISTÓRICO E LIQUIDEZ**: Busque o preço de mercado atual e realista do produto em grandes varejistas do Brasil. Sua sugestão DEVE ser o preço mais baixo da FAIXA HISTÓRICA DO PRODUTO, focado na liquidez máxima (venda rápida). **Para produtos populares como 'Whey Protein', a sugestão de preço para o estado 'Novo (lacrado)' DEVE ser o mais próximo possível de R$ 90,00, pois preços acima de R$ 130 desestimulam a compra.** "
    "Para outros produtos, aplique essa mesma lógica de PREÇO MÍNIMO PARA VENDA RÁPIDA, ignorando o preço cheio."
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
# FUNÇÃO DE GERAÇÃO
# ===============================================
def generate_cliqlinks_response(prompt):
    
    for attempt in range(3):
        try:
            with st.spinner("CliqLinks AI está analisando o mercado e criando sua estratégia..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt],
                    # A função de geração usa o prompt de sistema CORRIGIDO.
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

# (O restante do código Streamlit permanece o mesmo)
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
    
    # 💡 NOVO: MENSAGEM DE ACESSO DEV
    if is_developer_access:
        st.success("💻 Modo Desenvolvedor ATIVO!")
        st.markdown("**Ideias Geradas:** ILIMITADO")
    else:
        st.markdown(f"**Ideias Geradas (Grátis):** **{st.session_state.idea_count}** de **7**")
        st.progress(st.session_state.idea_count / 7)
    
    # IMPLEMENTAÇÃO DE PAGAMENTO (R$ 5,00
    # O restante do código de interface do Streamlit (principal e barra lateral) deve ser colado aqui,
    # começando da linha "IMPLEMENTAÇÃO DE PAGAMENTO" até o final do seu código Streamlit.
    # Como você só me forneceu o início da barra lateral, vou deixar o final em comentário.
    # ...
