import html
import re
from pathlib import Path

import requests


PADRAO_ERRO = re.compile(r"\[(?:ERROR|FATAL)\]")


class TelegramError(Exception):
    pass


class LogTail:
    def __init__(self, caminho_arquivo: str) -> None:
        self.caminho = Path(caminho_arquivo)
        stat = self.caminho.stat()
        if not self.caminho.is_file():
            raise OSError(f"{self.caminho} não é um arquivo.")

        self._identidade = (stat.st_dev, stat.st_ino)
        self._posicao = stat.st_size

    def ler_novas_linhas(self) -> list[str]:
        stat = self.caminho.stat()
        identidade = (stat.st_dev, stat.st_ino)
        if identidade != self._identidade or stat.st_size < self._posicao:
            self._identidade = identidade
            self._posicao = 0

        with self.caminho.open("r", encoding="utf-8", errors="replace") as arquivo:
            arquivo.seek(self._posicao)
            linhas = arquivo.readlines()
            self._posicao = arquivo.tell()

        return linhas


def enviar_alerta(token: str, chat_id: str, mensagem: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        raise TelegramError("Falha de comunicação ao enviar alerta ao Telegram.") from exc

    if not response.ok:
        raise TelegramError(f"Telegram recusou o alerta (HTTP {response.status_code}).")

    try:
        resultado = response.json()
    except ValueError as exc:
        raise TelegramError("O Telegram retornou uma resposta inválida.") from exc

    if not isinstance(resultado, dict) or not resultado.get("ok"):
        descricao = resultado.get("description", "erro não especificado") if isinstance(resultado, dict) else "resposta inválida"
        raise TelegramError(f"Telegram não confirmou o envio: {descricao}")


def formatar_mensagem(linha_log: str) -> tuple[str, str, str]:
    linha_limpa = linha_log.strip()

    if "[FATAL]" in linha_limpa:
        icone, nivel = "🛑", "FATAL"
    else:
        icone, nivel = "⚠️", "ERROR"

    mensagem = (
        f"{icone} <b>ALERTA DE LOG - {nivel}</b>\n\n"
        f"<b>Servidor:</b> Produção\n"
        f"<b>Detalhes:</b>\n<code>{html.escape(linha_limpa)}</code>"
    )

    return icone, nivel, mensagem
