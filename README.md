# 📚 Ingestão e Busca Semântica com LangChain e Postgres

> Um sistema de linha de comando (CLI) que lê um PDF, indexa seu conteúdo em um banco vetorial e responde perguntas **exclusivamente** com base no que está no documento — sem alucinações, sem conhecimento externo.

Projeto desenvolvido como desafio prático de **RAG** (Retrieval-Augmented Generation).

Combina **Python**, **LangChain**, **PostgreSQL + pgVector** e a API do **Google Gemini**.

---

## 🎯 O que esta aplicação faz?

1. 📄 Lê um arquivo PDF e divide seu conteúdo em pedaços menores (*chunks*)

2. 🧮 Converte cada chunk em um vetor numérico (*embedding*)

3. 🐘 Armazena esses vetores no PostgreSQL, usando a extensão **pgVector**

4. ❓ Recebe perguntas do usuário via terminal

5. 🔍 Busca, por similaridade semântica, os 10 trechos mais relevantes para a pergunta

6. 🤖 Envia esses trechos + a pergunta para um LLM (Gemini), que responde **somente** com base neles

Se a resposta não estiver explicitamente no PDF, a aplicação recusa educadamente.

Ela nunca inventa e nunca completa com conhecimento próprio do modelo.

### 💬 Exemplo prático

```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento da empresa SuperTechIABrazil é de R$ 10.000.000,00.

---

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## 🧠 Objetivo do desafio

Praticar o padrão RAG de ponta a ponta.

Isso inclui: ingestão de documentos, geração de embeddings, busca vetorial e geração de respostas com *grounding* — ou seja, respostas ancoradas apenas no contexto recuperado, sem alucinação.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Papel no projeto |
|---|---|
| 🐍 **Python** | Linguagem da aplicação |
| 🦜 **LangChain** | Orquestração de document loaders, embeddings, vector store e prompts |
| 🐘 **PostgreSQL + pgVector** | Armazenamento e busca por similaridade dos vetores |
| 🐳 **Docker & Docker Compose** | Execução do banco de dados, isolada e reprodutível |
| ✨ **Google Gemini** | Modelo de embedding (`gemini-embedding-001`) e modelo de chat (`gemini-3.6-flash`) |

## 🏗️ Como funciona (arquitetura)

O fluxo acontece em duas fases independentes.

**Fase 1 — Ingestão** (`src/ingest.py`, roda uma única vez):

```
document.pdf
     │
     ▼
PyPDFLoader
     │
     ▼
RecursiveCharacterTextSplitter
     │      (chunks de 1000 caracteres, com 150 de sobreposição)
     ▼
Embeddings (Gemini)
     │
     ▼
PostgreSQL + pgVector
```

**Fase 2 — Busca e resposta** (`src/search.py` + `src/chat.py`, roda a cada pergunta):

```
Pergunta do usuário
     │
     ▼
Embedding da pergunta
     │
     ▼
Busca no pgVector
     │      (similarity_search_with_score, k=10)
     ▼
Contexto + Prompt com regras de grounding
     │
     ▼
LLM (Gemini)
     │
     ▼
Resposta exibida no terminal
```

---

## ✅ Pré-requisitos

- **Python 3.11+** — [baixar aqui](https://www.python.org/downloads/) (versões anteriores não são compatíveis com as dependências fixadas em `requirements.txt`)
- **Docker Desktop** — [baixar aqui](https://www.docker.com/products/docker-desktop/)
- **Google API Key gratuita** — [obter em Google AI Studio](https://aistudio.google.com/apikey)

## ⚙️ Configuração e execução

**1. Clone o repositório e entre na pasta do projeto**
```bash
git clone <url-do-repositorio>
cd mba-ia-desafio-ingestao-busca
```

**2. Crie e ative um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Copie o template e preencha com seus dados:
```bash
cp .env.example .env
```

| Variável | Descrição |
|---|---|
| `GOOGLE_API_KEY` | Sua chave da API do Google AI Studio |
| `GOOGLE_EMBEDDING_MODEL` | Modelo de embedding (padrão: `models/gemini-embedding-001`) |
| `GOOGLE_LLM_MODEL` | Modelo de chat (padrão: `gemini-3.6-flash`) |
| `DATABASE_URL` | String de conexão com o Postgres (ex.: `postgresql+psycopg://postgres:postgres@localhost:5432/rag`) |
| `PG_VECTOR_COLLECTION_NAME` | Nome da coleção de vetores no pgVector |
| `PDF_PATH` | Caminho do PDF a ser ingerido (padrão: `document.pdf`) |

**5. Suba o banco de dados**
```bash
docker compose up -d
```

**6. Rode a ingestão do PDF** (uma única vez, ou sempre que trocar de documento/modelo de embedding)
```bash
python src/ingest.py
```

**7. Inicie o chat**
```bash
python src/chat.py
```

Digite sua pergunta e pressione Enter. Para encerrar, digite `sair`, `exit` ou `quit`.

> ⚠️ **Atenção:** se você trocar de modelo de embedding depois de já ter ingerido dados, a dimensão dos vetores muda e a busca deixa de funcionar. Nesse caso, apague a coleção (ou o volume `postgres_data`) e rode a ingestão novamente.

---

## 📁 Estrutura do projeto

```
├── docker-compose.yml    # Sobe o PostgreSQL com pgVector
├── requirements.txt      # Dependências do projeto
├── .env.example          # Template das variáveis de ambiente
├── document.pdf          # PDF de exemplo, usado na ingestão
├── src/
│   ├── ingest.py         # Lê o PDF, gera embeddings e grava no pgVector
│   ├── search.py         # Busca semântica + montagem do prompt + chamada ao LLM
│   └── chat.py           # Interface de linha de comando (CLI)
└── README.md
```

## 🧪 Cenários testados

| Cenário | Comportamento esperado |
|---|---|
| Pergunta com resposta explícita no PDF | Responde corretamente, citando a informação do documento |
| Pergunta sem resposta no PDF | Recusa fixa: *"Não tenho informações necessárias para responder sua pergunta."* |
| Pergunta parcialmente relacionada | Responde só a parte presente no contexto, recusando o restante |
| Tentativa de usar conhecimento externo (ex.: *"qual a capital da França?"*) | Recusa, mesmo sendo uma pergunta de conhecimento geral |

---

## 📄 Licença

Este projeto foi desenvolvido para o MBA de Engenharia de Software com IA - Full Cycle.

---

🚀 Desenvolvido por **Valéria Sousa** ([@ValSousa](https://github.com/ValSousa))
