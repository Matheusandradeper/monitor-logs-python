import requests
import time
import re
import os

def enviar_alerta(token: str, chat_id: str, mensagem: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")

def formatar_mensagem(linha_log: str) -> tuple:
    linha_limpa = linha_log.strip()
    
    if "[FATAL]" in linha_limpa:
        icone, nivel = "🛑", "FATAL"
    else:
        icone, nivel = "⚠️", "ERROR"
        
    mensagem = (
        f"{icone} <b>ALERTA DE LOG - {nivel}</b>\n\n"
        f"<b>Servidor:</b> Produção\n"
        f"<b>Detalhes:</b>\n<code>{linha_limpa}</code>"
    )
    
    return icone, nivel, mensagem

def verificar_log(caminho_arquivo: str, token: str, chat_id: str, placeholder_ui) -> None:
    if not os.path.exists(caminho_arquivo):
        placeholder_ui.error(f"❌ Arquivo {caminho_arquivo} não encontrado.")
        return

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        
        while True:
            linha = f.readline()
            
            if not linha:
                time.sleep(1)
                continue
                
            if re.search(r'\[ERROR\]|\[FATAL\]', linha):
                icone, nivel, mensagem = formatar_mensagem(linha)
                
                enviar_alerta(token, chat_id, mensagem)
                
                placeholder_ui.warning(f"**{icone} Alerta {nivel} enviado:**\n`{linha.strip()}`")