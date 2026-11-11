import streamlit as st

from monitor_logs import (
    PADRAO_ERRO,
    LogTail,
    TelegramError,
    enviar_alerta,
    formatar_mensagem,
)


st.set_page_config(page_title="Monitor N2", page_icon="🛡️", layout="wide")

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

if "monitor_ativo" not in st.session_state:
    st.session_state.monitor_ativo = False
if "alertas" not in st.session_state:
    st.session_state.alertas = []

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111646.png", width=60)
    st.header("Configurações do Bot")

    token = st.text_input("Token de Acesso", type="password", help="Token gerado pelo @BotFather")
    chat_id = st.text_input("Chat ID", help="ID numérico do seu usuário do Telegram")
    arquivo_log = st.text_input("Arquivo de Log", value="server.log")

    st.divider()
    st.markdown("**Como usar:**\n1. Preencha os dados.\n2. Inicie o monitoramento.\n3. Adicione `[ERROR]` ou `[FATAL]` ao log.")

    iniciar = st.button(
        "▶️ Iniciar Monitoramento",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.monitor_ativo,
    )
    parar = st.button(
        "⏹️ Parar Monitoramento",
        use_container_width=True,
        disabled=not st.session_state.monitor_ativo,
    )

if parar:
    st.session_state.monitor_ativo = False

if iniciar:
    if not token or not chat_id:
        st.error("⚠️ Preencha o Token e o Chat ID na barra lateral para começar.")
    elif not arquivo_log.strip():
        st.error("Informe o caminho do arquivo de log.")
    else:
        try:
            st.session_state.monitor_log = LogTail(arquivo_log.strip())
        except OSError as exc:
            st.error(f"Não foi possível abrir o arquivo de log: {exc}")
        else:
            st.session_state.telegram_token = token
            st.session_state.telegram_chat_id = chat_id
            st.session_state.alertas = []
            st.session_state.monitor_ativo = True

st.markdown('<p class="big-font">🛡️ Monitor de Logs N2</p>', unsafe_allow_html=True)
st.markdown("Sistema proativo de monitoramento de servidores com integração ao Telegram.")
st.divider()


@st.fragment(run_every=1)
def atualizar_monitoramento() -> None:
    if not st.session_state.monitor_ativo:
        return

    st.success(f"Monitoramento ativo no arquivo: `{arquivo_log}`")

    try:
        linhas = st.session_state.monitor_log.ler_novas_linhas()
    except OSError as exc:
        st.error(f"Falha ao ler o arquivo de log: {exc}")
        return

    for linha in linhas:
        if not PADRAO_ERRO.search(linha):
            continue

        icone, nivel, mensagem = formatar_mensagem(linha)
        try:
            enviar_alerta(
                st.session_state.telegram_token,
                st.session_state.telegram_chat_id,
                mensagem,
            )
        except TelegramError as exc:
            st.session_state.alertas.append(
                {"status": "erro", "icone": icone, "nivel": nivel, "linha": linha.strip(), "mensagem": str(exc)}
            )
        else:
            st.session_state.alertas.append(
                {"status": "enviado", "icone": icone, "nivel": nivel, "linha": linha.strip()}
            )

    st.session_state.alertas = st.session_state.alertas[-20:]
    st.subheader("Últimos Alertas Detectados")
    if not st.session_state.alertas:
        st.caption("Nenhum erro novo detectado.")
    for alerta in reversed(st.session_state.alertas[-20:]):
        if alerta["status"] == "enviado":
            st.success(f"{alerta['icone']} Alerta {alerta['nivel']} enviado")
        else:
            st.error(f"Falha ao enviar alerta {alerta['nivel']}: {alerta['mensagem']}")
        st.code(alerta["linha"])


atualizar_monitoramento()
