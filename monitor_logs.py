import requests
import time
import re
import os

def enviar_alerta(token, chat_id, mensagem):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # O parâmetro parse_mode="HTML" permite usar tags como <b> e <code> no Telegram
    payload = {
        "chat_id": chat_id, 
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def verificar_log(caminho_arquivo, token, chat_id, placeholder_ui):
    if not os.path.exists(caminho_arquivo):
        placeholder_ui.error(f"❌ Arquivo {caminho_arquivo} não encontrado.")
        return

    # Move o ponteiro para o final do arquivo para ler apenas o que for novo
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        
        while True:
            linha = f.readline()
            if not linha:
                time.sleep(1) # Espera 1 segundo
                continue
                
            # Verifica se é ERROR ou FATAL
            if re.search(r'\[ERROR\]|\[FATAL\]', linha):
                linha_limpa = linha.strip()
                
                # Formatação bonita para o Telegram
                if "[FATAL]" in linha_limpa:
                    icone = "🛑"
                    nivel = "FATAL"
                else:
                    icone = "⚠️"
                    nivel = "ERROR"
                
                # Usando HTML para formatar o texto
                mensagem = (
                    f"{icone} <b>ALERTA DE LOG - {nivel}</b>\n\n"
                    f"<b>Servidor:</b> Produção\n"
                    f"<b>Detalhes:</b>\n<code>{linha_limpa}</code>"
                )
                
                enviar_alerta(token, chat_id, mensagem)
                
                # Atualiza a tela do Streamlit (também formatado em Markdown)
                placeholder_ui.warning(f"**{icone} Alerta {nivel} enviado:**\n`{linha_limpa}`")