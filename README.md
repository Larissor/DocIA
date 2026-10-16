# 📚 DocIA — Assistente Inteligente de Documentos

**Consulte seus documentos e encontre informações com o auxílio da Inteligência Artificial.**

O DocIA é um projeto de assistente inteligente baseado em **RAG (Retrieval-Augmented Generation)**, desenvolvido com Python e modelos de IA executados localmente. A proposta é permitir que o usuário faça perguntas sobre documentos e receba respostas fundamentadas no conteúdo recuperado.

> 🚧 **Status:** Em desenvolvimento.

## ✨ Objetivos do projeto

- 📄 Processar documentos e extrair seu conteúdo.
- 🔎 Encontrar trechos relevantes para responder às perguntas.
- 🤖 Utilizar modelos de linguagem para gerar respostas contextualizadas.
- 🔐 Priorizar uma arquitetura local, com maior controle sobre os dados.
- 🧪 Desenvolver uma aplicação organizada, testável e preparada para evoluir.

## 🧠 Como funciona?

O projeto segue o conceito de RAG, combinando recuperação de informações com geração de respostas.

1. **Entrada:** o usuário fornece um documento compatível.
2. **Processamento:** o texto é extraído e dividido em trechos menores (*chunks*).
3. **Vetorização:** os trechos são convertidos em embeddings.
4. **Recuperação:** o sistema busca os trechos mais relevantes para a pergunta.
5. **Geração:** o modelo de linguagem utiliza o contexto recuperado para elaborar uma resposta.

## 🛠️ Tecnologias

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal |
| FastAPI | Construção da API |
| Ollama | Execução local de modelos de IA |
| ChromaDB | Armazenamento e busca vetorial |
| PyMuPDF | Extração de texto de PDFs |
| Streamlit | Interface web planejada |
| Pytest | Testes automatizados |
| Git e GitHub | Versionamento e colaboração |

*As tecnologias e funcionalidades devem ser atualizadas conforme forem implementadas e validadas no projeto.*

## 🏗️ Arquitetura prevista

A organização pode evoluir durante o desenvolvimento. Uma estrutura de referência é:

```text
DocIA/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   └── repositories/
├── frontend/
├── tests/
├── data/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Como executar

### Pré-requisitos

- Python 3.11 ou superior
- [Ollama](https://ollama.com/) instalado
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/Larissor/DocIA.git
cd DocIA
```

### 2. Crie e ative um ambiente virtual

**Windows — PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows — Prompt de Comando (CMD):**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o Ollama

Com o Ollama instalado e em execução, baixe os modelos utilizados pelo projeto:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:1b
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`, mantendo os nomes das variáveis compatíveis com a configuração da aplicação.

Exemplo:

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:1b
EMBEDDING_MODEL=nomic-embed-text
CHROMA_PATH=./data/chroma
TOP_K=4
```

**Importante:** não envie arquivos `.env` com dados privados, chaves de API ou credenciais para o GitHub.

### 6. Execute a aplicação

Quando os arquivos de entrada estiverem implementados, os comandos previstos são:

**API:**

```bash
uvicorn app.main:app --reload
```

**Interface web:**

```bash
streamlit run frontend/streamlit_app.py
```

Esses comandos dependem da existência dos respectivos arquivos no projeto.

## 🧪 Testes

O projeto prevê testes automatizados para validar o processamento de documentos e outros componentes.

Quando os testes estiverem configurados, execute:

```bash
pytest
```

## 🔒 Privacidade e segurança

O DocIA prioriza o uso de modelos locais e o controle dos dados processados. A privacidade efetiva depende da implementação, das configurações e dos serviços utilizados.

- Não versionar arquivos com informações confidenciais.
- Manter documentos pessoais e bancos vetoriais locais fora do repositório.
- Validar os arquivos recebidos antes do processamento.
- Tratar erros e entradas inválidas de forma segura.

## 🗺️ Próximas etapas

- [ ] Implementar e validar o processamento de documentos.
- [ ] Desenvolver a divisão do texto em chunks.
- [ ] Integrar a geração de embeddings.
- [ ] Implementar a busca vetorial com ChromaDB.
- [ ] Integrar a recuperação de contexto à geração de respostas.
- [ ] Desenvolver os endpoints da API.
- [ ] Criar a interface de consulta.
- [ ] Adicionar testes automatizados e documentação da API.

> As etapas devem ser marcadas como concluídas à medida que forem implementadas e testadas.

## 👨‍💻 Desenvolvedores

- **[Larissor](https://github.com/Larissor)** — Desenvolvimento do projeto.
- **Zoddick** — Desenvolvimento do projeto.

## 📄 Licença

A licença do projeto ainda deve ser definida. Até lá, consulte as informações do repositório antes de reutilizar ou distribuir o código.

---

⭐ **DocIA** — Explorando as possibilidades da Inteligência Artificial aplicada à consulta de documentos.