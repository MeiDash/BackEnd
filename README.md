# Backend API

## 📋 Descrição

Backend completo desenvolvido com **FastAPI** para gerenciamento. Este projeto é o backend de um aplicativo full-stack, com frontend em React + TypeScript.

## 🚀 Recursos

- ✅ Autenticação com JWT
- ✅ Gerenciamento de usuários (CRUD)
- ✅ Criptografia de senhas com bcrypt
- ✅ Validação de dados com Pydantic
- ✅ Banco de dados com SQLAlchemy ORM
- ✅ CORS configurável para integração com frontend
- ✅ API documentada com Swagger/OpenAPI
- ✅ Estrutura modular e escalável
- ✅ Testes automatizados
- ✅ Variáveis de ambiente

## 📁 Estrutura do Projeto

```
BackEnd/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py          # Rotas de autenticação
│   │   │   ├── users.py         # Rotas de usuários
│   │   │   ├── nota_fiscal.py   # Rotas notas fiscais
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py            # Configurações da aplicação
│   │   ├── security.py          # Funções de segurança e JWT
│   │   └── __init__.py
│   ├── db/
│   │   ├── database.py          # Configuração do banco de dados
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py              # Modelo de usuário (SQLAlchemy)
│   │   ├── nota_fiscal.py       # Modelo de nota fiscal e métricas (SQLAlchemy)
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py              # Schemas Pydantic para validação
│   │   ├── base.py              # CamelModel para resolver importação circular 
│   │   ├── nota_fiscal.py       # Schemas para nota fiscal e métricas
│   │   └── __init__.py
│   ├── services/
│   │   ├── user_service.py        # Lógica de negócio de usuários
│   │   ├── email_service.py       # Lógica de negócio de envio de email
│   │   ├── nota_fiscal_service.py # Lógica de negócio de notas fiscais e métricas
│   │   └── __init__.py
│   ├── utils/
│   │   ├── response.py          # Utilitários de resposta e paginação
│   │   └── __init__.py
│   ├── main.py                  # Aplicação principal FastAPI
|   ├── dependencies.py          # Lógica de get_current_user
│   └── __init__.py
├── tests/
│   ├── test_api.py              # Testes da API
│   ├── conftest.py              # Configuração do pytest
│   └── __init__.py
├── .env.example                 # Variáveis de ambiente de exemplo
├── .gitignore                   # Arquivos ignorados pelo git
├── requirements.txt             # Dependências do projeto
├── run.py                       # Script para executar a aplicação
└── README.md                    # Este arquivo
```

## 🔧 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- PostgreSQL (instalado e rodando localmente)

### Passos

1. **Clonar o repositório**
```bash
git clone <url-do-repositorio>
cd BackEnd
```

2. **Criar ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Configurar PostgreSQL**
   - Instale e inicie o PostgreSQL (ex.: via pgAdmin ou linha de comando).
   - Crie um banco de dados vazio (ex.: nome "MeiDAsh" ou outro de sua escolha).

5. **Configurar variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com suas credenciais PostgreSQL (ex.: DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/MeiDAsh)

# Edite a senha do e-mail do .env com a senha de app que vai ser fornecida.
```

6. **Inicializar banco de dados (opcional, para dados de teste)**
```bash
python init_db.py
```

7. **Executar a aplicação**
```bash
python run.py
```

A API estará disponível em `http://localhost:8000`

## 📚 Endpoints

### Autenticação

- `POST /api/auth/login` - Login e obtenção de token JWT
- `POST /api/auth/logout` - Logout

### Usuários

- `POST /api/users` - Criar novo usuário
- `GET /api/users` - Listar todos os usuários (com paginação)
- `GET /api/users/{user_id}` - Obter detalhes de um usuário
- `PUT /api/users/{user_id}` - Atualizar usuário
- `DELETE /api/users/{user_id}` - Deletar usuário

### Notas fiscais

- `POST /api/nfe` - Cadastrar nova nota fiscal

### Utilitários

- `GET /` - Informações da API
- `GET /health` - Health check

## 📖 Documentação API

A documentação interativa está disponível em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗄️ Banco de Dados

### Modelo de Usuário

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  username VARCHAR UNIQUE NOT NULL,
  full_name VARCHAR,
  hashed_password VARCHAR NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

### Criar tabelas automaticamente

As tabelas são criadas automaticamente ao iniciar a aplicação com base nos modelos SQLAlchemy (ex.: `app/models/user.py`). Não é necessário criar manualmente no pgAdmin.

### Dados de teste

Execute `python init_db.py` para inserir usuários de teste (admin@example.com / admin123 e test@example.com / test123). Isso é opcional e só insere se não existirem.

## 👥 Colaboração e Desenvolvimento

### Para outros desenvolvedores

1. **Configure seu PostgreSQL local**: Crie um banco vazio (mesmo nome ou diferente, ajustado no `.env`).
2. **Copie o `.env.example`** para `.env` e ajuste as credenciais locais (não compartilhe senhas reais).
3. **Estrutura idêntica**: As tabelas serão criadas automaticamente com a mesma estrutura (campos, índices) definida no código.
4. **Dados independentes**: Cada dev tem seus próprios dados locais; use `init_db.py` para dados consistentes de teste.
5. **Não versionar `.env`**: Ele está no `.gitignore` para proteger credenciais.

### Boas práticas

- Use bancos locais para desenvolvimento.
- Para produção, configure variáveis de ambiente no servidor (ex.: Azure Key Vault).
- Evite inserir dados de teste em produção; use migrações para esquemas.

## 🔐 Segurança

- **Senhas**: Criptografadas com bcrypt (limite de 72 bytes UTF-8 por senha)
- **Autenticação**: JWT (JSON Web Tokens)
- **CORS**: Configurável por domínio
- **Validação**: Pydantic schemas para todas as entradas

### Validações de Dados

- **Email**: Deve ser um endereço de email válido
- **Nome**: Mínimo 1, máximo 120 caracteres
- **Senha**: Mínimo 8 caracteres, máximo 72 bytes (UTF-8)
- **CNPJ**: Opcional, formato livre
- **Nome da Empresa**: Opcional, formato livre
- **Ocupação**: Opcional, formato livre

## 🧪 Testes

Para executar os testes:

```bash
# Todos os testes
python -m pytest tests/

# Com cobertura
python -m pytest tests/ --cov=app --cov-report=term-missing

# Teste específico
python -m pytest tests/test_api.py::TestUsers::test_create_user_success -v
```

## 🌐 Integração com Frontend

Para conectar com o frontend React/TypeScript:

1. Certifique-se que `ALLOWED_ORIGINS` no `.env` contém a URL do seu frontend
2. Use o endpoint `/docs` para explorar a API
3. Inclua o token JWT no header `Authorization: Bearer {token}` para requisições autenticadas

### Exemplo de chamada com fetch:

```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
});
const { access_token } = await response.json();

// Usar token
const userResponse = await fetch('http://localhost:8000/api/users/1', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 📦 Dependências Principais

- **FastAPI**: Framework web assíncrono
- **Uvicorn**: Servidor ASGI
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados
- **python-jose**: Implementação de JWT
- **passlib**: Hashing de senhas
- **psycopg2**: Driver PostgreSQL

## 🚀 Deploy

Para deploy em produção:

1. Defina `ENVIRONMENT=production` no `.env`
2. Use uma `SECRET_KEY` forte e aleatória
3. Configure o banco de dados PostgreSQL
4. Use um servidor ASGI como Gunicorn
5. Configure um reverse proxy como Nginx

### Exemplo com Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## 📝 Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste os valores:

```
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/MeiDAsh
SECRET_KEY=sua-chave-secreta-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
ENVIRONMENT=development
```

- **DATABASE_URL**: Use suas credenciais PostgreSQL locais.
- **SECRET_KEY**: Gere uma chave aleatória (ex.: via Python: `secrets.token_urlsafe(32)`).
- **ALLOWED_ORIGINS**: Adicione URLs do frontend para CORS.

## 🐛 Troubleshooting

### Erro de conexão com banco de dados

Verifique se o PostgreSQL está rodando e se as credenciais em `.env` estão corretas.

### Erro 422 na API

Valide os dados enviados de acordo com os schemas em `app/schemas/`.

### CORS error no frontend

Adicione a URL do seu frontend em `ALLOWED_ORIGINS` no `.env`.
