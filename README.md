# Desafio Beber - API de Busca Semântica RAG

API de busca semântica de documentos utilizando RAG (Retrieval-Augmented Generation), construída com FastAPI, MinIO e Elasticsearch.

## 📋 Sobre o Projeto

Esta aplicação permite fazer upload de documentos e realizar buscas semânticas utilizando embeddings. Os documentos são armazenados no MinIO para emular (Bucket S3) e os embeddings são indexados no Elasticsearch para permitir buscas por similaridade semântica.

## 🚀 Tecnologias

- **FastAPI**: Framework web assíncrono para Python
- **MinIO**: Armazenamento de objetos (S3-compatible)
- **Elasticsearch**: Banco de dados vetorial para busca semântica
- **Sentence Transformers**: Geração de embeddings usando modelos pré-treinados
- **Python 3.12+**: Linguagem de programação
- **UV**: Gerenciador de pacotes Python moderno

## 📁 Estrutura do Projeto

```
desafio_beber/
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile
├── src/
│   ├── application/          # Camada de aplicação
│   │   ├── dtos/             # Data Transfer Objects
│   │   └── use_cases/        # Casos de uso
│   ├── domain/               # Camada de domínio
│   │   ├── entities/         # Entidades de domínio
│   │   ├── exceptions/       # Exceções de domínio
│   │   └── repositories/     # Interfaces de repositórios
│   ├── infra/                # Camada de infraestrutura
│   │   ├── config/           # Configurações e DI
│   │   ├── routes/           # Rotas da API
│   │   └── services/         # Implementações de serviços
│   ├── main.py               # Ponto de entrada da aplicação
│   └── tests/                # Testes
├── env.example               # Exemplo de variáveis de ambiente
├── makefile                  # Comandos úteis
├── pyproject.toml            # Configuração do projeto
└── README.md                 # Este arquivo
```

## 🛠️ Pré-requisitos

- Python 3.12.7 ou superior
- Docker e Docker Compose
- UV (gerenciador de pacotes Python)

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/mitdua/desafio_beber
cd desafio_beber
```

### 2. Configure o ambiente

Execute o comando de setup que irá:
- Criar o arquivo `.env` a partir do `env.example`
- Instalar o UV (se necessário)
- Instalar as dependências do projeto

```bash
make setup
```

### 3. Inicie os serviços Docker

```bash
make docker-up
```

Isso irá iniciar:
- **MinIO** na porta 9000 (API) e 9001 (Console)
- **Elasticsearch** na porta 9200
- **Aplicação** na porta 8000

## 🎯 Uso

### Executar a aplicação


A API estará disponível em `http://localhost:8000`

### Documentação interativa

Acesse a documentação interativa da API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints

### Health Check

```bash
curl --request GET \
  --url http://localhost:8000/health 
```

Verifica o status da aplicação e dos serviços dependentes.

### Upload de Documentos

```bash
curl --request POST \
  --url http://localhost:8000/documents \
  --header 'Content-Type: multipart/form-data'
  --form files=@/rota/Documents/test.pdf
```

Envia um ou mais documentos para processamento. Formatos suportados:
- PDF (`.pdf`)
- Texto (`.txt`)
- Word (`.doc`, `.docx`)
- Excel (`.xls`, `.xlsx`)
- JSON (`.json`)


### Busca Semântica

```bash
curl --request POST \
  --url http://localhost:8000/query \
  --header 'Content-Type: application/json'
  --data '{
	"query": "test_query",
	"top_k": 2
}'
```

**Resposta:**

```json
{
  "query": "test_query",
  "results": [
    {
      "document": {
        "id": "uuid",
        "filename": "documento.pdf",
        "content": "...",
        "metadata": {},
        "created_at": "2024-01-01T00:00:00Z"
      },
      "score": 0.95,
      "rank": 1
    }
  ],
  "total_results": 1
}
```

## 🐳 Docker

### Comandos úteis

```bash
# Iniciar serviços
make docker-up

# Parar serviços
make docker-down

# Reiniciar serviços
make docker-restart

# Ver logs
make docker-logs
```

### Acessar serviços

- **MinIO Console**: http://localhost:9001
  - Usuário: (ou valor de `MINIO_ACCESS_KEY`)
  - Senha: (ou valor de `MINIO_SECRET_KEY`)

- **Elasticsearch**: http://localhost:9200


## 📝 Arquitetura

O projeto segue uma arquitetura em camadas:

1. **Domain**: Contém as entidades de negócio e interfaces de repositórios
2. **Application**: Contém os casos de uso e DTOs
3. **Infrastructure**: Contém as implementações concretas (repositórios, serviços, rotas)

A injeção de dependências é gerenciada através do `dependency-injector`.

## 🔧 Desenvolvimento

### Estrutura de Casos de Uso

- **UploadDocumentUseCase**: Processa o upload de documentos
  - Extrai o conteúdo do arquivo
  - Armazena no MinIO
  - Gera embeddings
  - Indexa no Elasticsearch

- **QueryDocumentsUseCase**: Realiza buscas semânticas
  - Gera embedding da query
  - Busca documentos similares no Elasticsearch
  - Retorna resultados ordenados por similaridade
