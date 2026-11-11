# 🚨 Monitor de Logs com Alerta no Telegram

> **Nota de aprendizado:** Este é o meu primeiro projeto prático focado em automação com Python, integração com APIs e criação de Bots. Ele foi desenvolvido como parte dos meus estudos contínuos para evoluir de Analista de Suporte para uma posição focada em Automação e Engenharia de Dados.

## 💡 O Motivo do Projeto (A "Dor" do Suporte)

Atuando na linha de frente do suporte N2, percebo que muitas vezes a equipe de TI só descobre que um servidor ou sistema caiu quando o usuário abre um chamado. Isso gera atraso no atendimento, quebra de SLA e uma experiência ruim para o cliente.

O objetivo deste projeto foi criar uma **Prova de Conceito (PoC)** de monitoramento proativo. A ideia é que um script "vigie" os logs do servidor em tempo real e, ao invés de esperar o chamado, avise a equipe de TI instantaneamente no celular através de um Bot no Telegram.

## ⚙️ O que o projeto faz

*   **Interface Web Amigável:** Uma tela construída em Streamlit onde o analista informa o Token do Bot, o Chat ID e o arquivo de log.
*   **Monitoramento Contínuo:** O Python verifica periodicamente apenas as linhas adicionadas depois que o monitoramento começa, sem bloquear a interface. O botão de parada encerra as verificações.
*   **Filtro com Regex:** Utiliza Expressões Regulares (Regex) para identificar padrões críticos, como as tags `[ERROR]` e `[FATAL]`.
*   **Alerta Formatado:** Ao encontrar um erro, envia uma mensagem formatada pela API do Telegram. O conteúdo do log é escapado para evitar que caracteres especiais sejam interpretados como HTML.
*   **Resiliência:** Reconhece truncamento e rotação do arquivo de log e exibe falhas de comunicação com o Telegram na interface.

## 🛠️ Tecnologias e Conceitos Utilizados

*   **Python 3**
*   **Streamlit:** Para a criação do dashboard web interativo.
*   **Requests:** Para o consumo da API HTTP do Telegram.
*   **Regex (re):** Para a busca de padrões no texto do log.
*   **Manipulação de Arquivos:** Leitura contínua (loop) com `seek()` para ler apenas o que é novo no arquivo.
*   **Git/GitHub:** Para versionamento e documentação.

## 🚀 Como testar este projeto na sua máquina

1. Clone este repositório.
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   # source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Crie um bot com o [@BotFather](https://t.me/BotFather) e obtenha o Token e o Chat ID.
4. Inicie o painel:
   ```bash
   streamlit run app_logs.py
   ```
5. Informe as credenciais e o caminho do arquivo. O monitor começa no final do arquivo para não reenviar erros antigos. Use **Parar Monitoramento** para encerrar.


## 📸 Demonstração

Abaixo, a prova de funcionamento do sistema em tempo real:

**1. Painel do Streamlit (Detectando o erro e enviando o alerta):**
![Painel Streamlit](images/print_painel.png)

**2. Notificação recebida no Telegram:**
<img src="images/print_telegram.png" width="400" alt="Alerta no Telegram">