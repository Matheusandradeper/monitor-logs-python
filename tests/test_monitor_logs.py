import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from monitor_logs import LogTail, TelegramError, enviar_alerta, formatar_mensagem


class LogTailTests(unittest.TestCase):
    def test_reads_only_lines_added_after_start(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "server.log"
            caminho.write_text("[INFO] antigo\n", encoding="utf-8")
            monitor = LogTail(str(caminho))

            self.assertEqual(monitor.ler_novas_linhas(), [])
            with caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write("[ERROR] novo\n")
            self.assertEqual(monitor.ler_novas_linhas(), ["[ERROR] novo\n"])
            self.assertEqual(monitor.ler_novas_linhas(), [])

    def test_reads_from_start_after_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "server.log"
            caminho.write_text("x" * 100, encoding="utf-8")
            monitor = LogTail(str(caminho))
            caminho.write_text("[FATAL] arquivo reiniciado\n", encoding="utf-8")

            self.assertEqual(monitor.ler_novas_linhas(), ["[FATAL] arquivo reiniciado\n"])

    def test_reads_new_file_after_rotation(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "server.log"
            substituto = Path(diretorio) / "server.log.new"
            caminho.write_text("[INFO] original\n", encoding="utf-8")
            monitor = LogTail(str(caminho))
            substituto.write_text("[ERROR] rotacionado\n", encoding="utf-8")
            os.replace(substituto, caminho)

            self.assertEqual(monitor.ler_novas_linhas(), ["[ERROR] rotacionado\n"])


class TelegramTests(unittest.TestCase):
    def test_escapes_log_content_for_html(self) -> None:
        _, nivel, mensagem = formatar_mensagem("[ERROR] <script>&")

        self.assertEqual(nivel, "ERROR")
        self.assertIn("&lt;script&gt;&amp;", mensagem)

    @patch("monitor_logs.requests.post")
    def test_reports_telegram_api_rejection(self, post: Mock) -> None:
        resposta = Mock(ok=True)
        resposta.json.return_value = {"ok": False, "description": "chat not found"}
        post.return_value = resposta

        with self.assertRaisesRegex(TelegramError, "chat not found"):
            enviar_alerta("token", "chat", "mensagem")

    @patch("monitor_logs.requests.post")
    def test_hides_token_from_network_errors(self, post: Mock) -> None:
        requests_error = requests.ConnectionError("failed")
        post.side_effect = requests_error

        with self.assertRaises(TelegramError) as contexto:
            enviar_alerta("secret-token", "chat", "mensagem")

        self.assertNotIn("secret-token", str(contexto.exception))
        self.assertIs(contexto.exception.__cause__, requests_error)


if __name__ == "__main__":
    unittest.main()
