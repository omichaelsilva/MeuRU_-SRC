# Sistema de Recarga e Gerenciamento de créditos digitais (RU) — UFCAT

<p align="center">
  <img <img width="379" height="205" alt="image" src="https://github.com/user-attachments/assets/1ef56353-afad-4f0d-98ec-354de26d26e3" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white"/>
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white"/>
</p>

> Sistema web completo de gerenciamento de créditos e controle de acesso ao Restaurante Universitário da Universidade Federal de Catalão (UFCAT), desenvolvido com FastAPI, SQLAlchemy e Jinja2. Esse é um protótipo para o sistema de créditos voltado ao RU para melhorar o que diz respeito a praticidade e bom gerenciamento do mesmo. Importante citar que esse é meu projeto de conclusão de curso do curso de ciências da computação pela UFCAT. 

---

## Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Configuração](#instalação-e-configuração)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Uso](#uso)
- [Modelos de Dados](#modelos-de-dados)
- [Segurança](#segurança)
- [API e Rotas](#api-e-rotas)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Visão Geral

O **Sistema RU** é uma aplicação web institucional desenvolvida para modernizar e digitalizar a gestão operacional do Restaurante Universitário da UFCAT. O sistema substitui controles manuais por uma plataforma centralizada que gerencia créditos alimentares, controle de acesso, emissão de relatórios e notificações automatizadas.

A solução contempla dois perfis de acesso distintos: **Alunos**, que acompanham seus créditos e histórico de refeições, e **Administradores**, que gerenciam cadastros, recargas, cardápios e métricas operacionais.

---

## Funcionalidades

### Portal do Aluno

| Funcionalidade | Descrição |
|---|---|
| Autenticação | Login via matrícula + senha com proteção JWT |
| Dashboard | Saldo de créditos, gráfico de consumo semanal (8 semanas) |
| Histórico | Consulta e filtro de refeições por tipo e período |
| Exportação | Download do histórico de transações em CSV |
| Primeiro Acesso | Fluxo de cadastro de senha no primeiro login |
| Recuperação de Senha | Envio de link de redefinição por e-mail |

### Portal Administrativo

| Funcionalidade | Descrição |
|---|---|
| Dashboard KPIs | Alunos ativos, refeições do dia, recargas e créditos totais |
| Gestão de Alunos | Listagem, busca, edição de créditos, categoria e status |
| Histórico Global | Visualização consolidada de refeições e recargas |
| Gestão de Cardápio | Editor diário (prato, acompanhamentos, sobremesa) |
| Métricas de Satisfação | Pesquisas automáticas via WhatsApp (escala 1–5) |
| Controle de Desperdício | Registro de nível de desperdício por refeição (baixo/médio/alto) |
| Alertas de Pico | Notificações para fluxos intensos (>15 acessos em 10 min) |
| Gestão de Administradores | Cadastro e controle de funções (super_admin / admin / operador) |

### Notificações Automatizadas

- **E-mail**: Abertura do RU com cardápio do dia (11h almoço / 19h jantar) e aviso de fechamento
- **WhatsApp (Twilio)**: Pesquisa de satisfação 30 min após a refeição e alertas de pico para administradores

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cliente (Browser)                       │
│              Jinja2 Templates + Tailwind CSS + JS               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                       FastAPI (ASGI)                            │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ auth_routes │  │ aluno_routes │  │    admin_routes       │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Serviços: Auth · Email · WhatsApp · Scheduler    │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQLAlchemy ORM
┌──────────────────────────▼──────────────────────────────────────┐
│                    SQLite / PostgreSQL                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tecnologias Utilizadas

| Camada | Tecnologia | Versão |
|---|---|---|
| Backend | Python | 3.11+ |
| Framework Web | FastAPI | 0.110+ |
| ORM | SQLAlchemy | 2.x |
| Banco de Dados | SQLite (dev) / PostgreSQL (prod) | — |
| Templates | Jinja2 | 3.x |
| CSS | Tailwind CSS (CDN) | 3.x |
| Autenticação | JWT + bcrypt | — |
| Agendador | APScheduler | 3.x |
| WhatsApp | Twilio | — |
| IA Integrada | Anthropic Claude API | — |

---

## Estrutura do Projeto

```
Programa/
├── populate_alunos.py          # Script de seed para dados de teste
├── ru_system/
│   ├── main.py                 # Ponto de entrada da aplicação
│   ├── config.py               # Configurações e variáveis de ambiente
│   ├── database.py             # Configuração do SQLAlchemy
│   ├── models.py               # Modelos ORM (12 entidades)
│   ├── schemas.py              # Schemas Pydantic para validação
│   ├── auth.py                 # JWT, bcrypt, rate limiting, CSRF
│   ├── email_service.py        # Serviço de envio de e-mails
│   ├── scheduler.py            # Agendamento de alertas automáticos
│   ├── whatsapp_bot.py         # Integração Twilio WhatsApp
│   ├── seed.py                 # Dados iniciais de teste
│   ├── requirements.txt        # Dependências Python
│   ├── .env.example            # Template de variáveis de ambiente
│   ├── routers/
│   │   ├── auth_routes.py      # Login, recuperação de senha
│   │   ├── aluno.py            # Rotas do portal do aluno
│   │   ├── admin.py            # Rotas do portal administrativo
│   │   └── webhook.py          # Webhook para respostas WhatsApp
│   ├── templates/              # Templates Jinja2
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── admin/
│   │   └── aluno/
│   └── static/
│       ├── css/custom.css
│       ├── js/app.js
│       └── img/                # Identidade visual UFCAT
└── Imagens/                    # Logos institucionais
```

---

## Instalação e Configuração

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/ru-system-ufcat.git
cd ru-system-ufcat
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r ru_system/requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp ru_system/.env.example ru_system/.env
# Edite o arquivo .env com suas credenciais
```

### 5. Inicialize o banco de dados e dados de teste

```bash
# Inicia a aplicação (cria o banco automaticamente)
uvicorn ru_system.main:app --reload

# Em outro terminal, popule com dados de teste
python populate_alunos.py
```

### 6. Acesse a aplicação

```
http://localhost:8000
```

**Credenciais de teste:**

| Perfil | Matrícula/Login | Senha |
|---|---|---|
| Super Admin | `admin` | `admin123` |
| Operador | `operador` | `op123` |
| Aluno (exemplo) | `2021001` | `senha123` |

---

## Variáveis de Ambiente

Crie o arquivo `ru_system/.env` baseado em `.env.example`:

```env
# Segurança
SECRET_KEY=sua-chave-secreta-jwt-aqui

# Banco de Dados (SQLite padrão ou PostgreSQL em produção)
DATABASE_URL=sqlite:///./ru.db

# E-mail (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

---

## Modelos de Dados

### Tabelas Principais

| Modelo | Descrição |
|---|---|
| `Student` | Alunos: matrícula, créditos, categoria, status |
| `Admin` | Administradores: função (super_admin / admin / operador) |
| `MealHistory` | Histórico de refeições por aluno |
| `RechargeHistory` | Histórico de recargas (recarga / remoção / ajuste) |
| `RecoveryToken` | Tokens de recuperação de senha (TTL: 1 hora) |
| `SatisfactionSurvey` | Pesquisas de satisfação enviadas via WhatsApp |
| `FoodWaste` | Registros de desperdício alimentar por refeição |
| `PeakMovement` | Eventos de fluxo intenso no RU |
| `DailyMenu` | Cardápio diário (almoço / jantar) |

### Categorias de Alunos e Valores de Refeição

| Categoria | Descrição | Valor (R$) |
|---|---|---|
| `bolsista` | Aluno bolsista | 0,00 (gratuito) |
| `subsidiado` | Aluno subsidiado | 4,00 |
| `aluno` | Aluno regular | 6,00 |
| `externo` | Usuário externo | 16,00 |

---

## Segurança

O sistema implementa as seguintes camadas de segurança:

- **Hashing de senhas**: bcrypt com 12 rounds de custo computacional
- **Autenticação stateless**: JWT armazenado em cookies HTTP-only (8h alunos / 12h admins)
- **Proteção CSRF**: Token anti-CSRF em todos os formulários POST
- **Rate Limiting**: Máximo de 5 tentativas de login por IP a cada 15 minutos
- **RBAC**: Controle de acesso baseado em funções (super_admin > admin > operador)
- **Tokens de recuperação**: Expiração em 1 hora e uso único

---

## API e Rotas

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Página de login |
| `POST` | `/login` | Autenticação unificada |
| `POST` | `/logout` | Encerramento de sessão |
| `GET/POST` | `/recuperar-senha` | Solicitação de recuperação |
| `GET/POST` | `/resetar-senha/{token}` | Redefinição via token |

### Portal do Aluno

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/aluno/dashboard` | Dashboard com saldo e gráfico |
| `GET` | `/aluno/historico` | Histórico de refeições |
| `GET` | `/aluno/historico/export` | Exportação CSV |

### Portal Administrativo

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/admin/dashboard` | KPIs operacionais |
| `GET/POST` | `/admin/alunos` | Gestão de alunos |
| `GET/POST` | `/admin/cardapio` | Editor de cardápio |
| `GET` | `/admin/satisfacao` | Métricas de satisfação |
| `GET/POST` | `/admin/admins` | Gestão de administradores |

---

## Contribuição

Contribuições são bem-vindas. Para contribuir:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## Licença

Este projeto é desenvolvido para fins acadêmicos e institucionais na **Universidade Federal de Catalão (UFCAT)**. Todos os direitos reservados.

---

<p align="center">
  Desenvolvido com dedicação para a comunidade acadêmica da UFCAT
</p>
