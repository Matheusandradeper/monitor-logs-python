import streamlit as st
from monitor_logs import verificar_log

st.set_page_config(page_title="Monitor N2", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #229ED9;
        color: white;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #1C85B8;
        color: white;
    }
    .big-font { 
        font-size: 32px !important; 
        font-weight: bold; 
        color: #229ED9; 
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111646.png", width=60)
    st.header("Configurações do Bot")
    
    token = st.text_input("Token de Acesso", type="password", help="Token gerado pelo @BotFather")
    chat_id = st.text_input("Chat ID", help="ID numérico do seu usuário do Telegram")
    arquivo_log = st.text_input("Arquivo de Log", value="server.log")
    
    st.divider()
    st.markdown("**Como usar:**\n1. Preencha os dados.\n2. Clique em Iniciar.\n3. Adicione `[ERROR]` no arquivo de log.")
    
    botao_iniciar = st.button("▶️ Iniciar Monitoramento", use_container_width=True, type="primary")

st.markdown('<p class="big-font">🛡️ Monitor de Logs N2</p>', unsafe_allow_html=True)
st.markdown("Sistema proativo de monitoramento de servidores com integração ao Telegram.")
st.divider()

if botao_iniciar:
    if not token or not chat_id:
        st.error("⚠️ **Atenção:** Preencha o Token e o Chat ID na barra lateral para começar.")
    else:
        st.success(f"✅ Monitoramento ativo no arquivo: `{arquivo_log}`")
        st.info("💡 **Dica:** Vá no VS Code, adicione uma linha com `[ERROR]` no arquivo e salve. O alerta aparecerá aqui e no seu Telegram.")
        
        st.subheader("Últimos Alertas Detectados")
        area_alertas = st.empty()
        
        verificar_log(arquivo_log, token, chat_id, area_alertas)