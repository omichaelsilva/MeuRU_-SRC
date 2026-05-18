# RU — Sistema de Recarga de Créditos

Sistema web para gerenciamento de créditos do Restaurante Universitário, desenvolvido com FastAPI + SQLite + Tailwind CSS.

---

## Requisitos

- Python 3.9+
- pip

---

## Instalação

```bash
# 1. Entre no diretório do projeto
cd ru_system

# 2. (Recomendado) Crie e ative um ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Configuração

Copie o arquivo de exemplo e edite conforme necessário:

```bash
cp .env.example .env
```

Variáveis disponíveis em `.env`:

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | (valor dev inseguro) | Chave para assinar JWTs |
| `BASE_URL` | `http://localhost:8000` | URL base (usada nos links de email) |
| `DATABASE_URL` | `sqlite:///./ru.db` | Banco de dados |
| `EMAIL_HOST` | `` (vazio) | Servidor SMTP (vazio = modo dev) |
| `EMAIL_PORT` | `587` | Porta SMTP |
| `EMAIL_USER` | `` | Usuário SMTP |
| `EMAIL_PASS` | `` | Senha SMTP |

> **Modo desenvolvimento (sem email):** deixe `EMAIL_HOST` vazio. Os links de recuperação de senha serão impressos no terminal.

---

## Populando o banco de dados

```bash
python seed.py
```

Isso cria:
- 1 super_admin
- 1 operador
- 5 alunos de teste
- Histórico de refeições e recargas dos últimos 30 dias

---

## Executando

```bash
uvicorn main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`.

---

## URLs de Acesso

| Área | URL |
|---|---|
| Login do Aluno | http://localhost:8000/login |
| Dashboard do Aluno | http://localhost:8000/aluno/dashboard |
| Histórico do Aluno | http://localhost:8000/aluno/historico |
| Login Admin | http://localhost:8000/admin/login |
| Dashboard Admin | http://localhost:8000/admin/dashboard |
| Alunos (admin) | http://localhost:8000/admin/alunos |
| Histórico Geral | http://localhost:8000/admin/historico |
| Gerenciar Admins | http://localhost:8000/admin/admins |

---

## Credenciais de Teste

### Admins

| Email | Senha | Função |
|---|---|---|
| admin@ru.edu.br | Admin@2024 | super_admin |
| operador@ru.edu.br | Oper@2024 | operador |

### Alunos

| Matrícula | Senha | Nome |
|---|---|---|
| 2024001 | Aluno@2024 | Ana Silva Santos |
| 2024002 | Aluno@2024 | Bruno Costa Oliveira |
| 2024003 | Aluno@2024 | Carla Mendes Ferreira |
| 2024005 | Aluno@2024 | Eduarda Pires Nunes |
| 2024004 | — | Daniel Rocha Lima (primeiro acesso pendente) |

> Os alunos com `primeiro_acesso=True` precisarão definir uma nova senha no primeiro login.

---

## Estrutura de Arquivos

```
ru_system/
├── main.py              # Entry point FastAPI
├── config.py            # Configurações e variáveis de ambiente
├── database.py          # SQLAlchemy setup (SQLite/PostgreSQL)
├── models.py            # ORM models
├── schemas.py           # Pydantic schemas
├── auth.py              # JWT, bcrypt, rate limiting, CSRF
├── email_service.py     # SMTP + fallback terminal
├── seed.py              # Dados iniciais
├── requirements.txt
├── .env.example
├── routers/
│   ├── auth_routes.py   # Login, logout, recuperação de senha
│   ├── aluno.py         # Área do aluno
│   └── admin.py         # Área administrativa
├── templates/           # Jinja2 + Tailwind CSS
└── static/              # CSS e JS customizados
```

---

## Migração para PostgreSQL

1. Instale o driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Configure no `.env`:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/ru_db
   ```

3. Crie o banco de dados no PostgreSQL e execute novamente `python seed.py`.

Não é necessário nenhuma outra alteração no código.

---

## Segurança

- Senhas com bcrypt (12 rounds)
- Tokens JWT HTTP-only cookies
- CSRF protection em todos os formulários POST
- Rate limiting: máx. 5 tentativas de login por IP em 15 minutos
- Separação completa entre área do aluno e área do admin
