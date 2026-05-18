"""
main.py — Entry point da aplicação RU.
Execute com: uvicorn main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from database import engine, Base, SessionLocal
from config import SECRET_KEY

# Importa todos os modelos para criar tabelas
import models  # noqa: F401

# Routers
from routers import auth_routes, aluno, admin
from routers import webhook

from scheduler import criar_scheduler

logger = logging.getLogger(__name__)

# ─── Criação das tabelas ──────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Migração segura: adiciona coluna telefone se não existir (SQLite) ───
def _migrar_colunas_alunos():
    from sqlalchemy import text, inspect
    with engine.connect() as conn:
        inspector = inspect(engine)
        colunas = [c["name"] for c in inspector.get_columns("alunos")]
        if "telefone" not in colunas:
            conn.execute(text("ALTER TABLE alunos ADD COLUMN telefone VARCHAR(20)"))
        if "categoria" not in colunas:
            conn.execute(text("ALTER TABLE alunos ADD COLUMN categoria VARCHAR(20) NOT NULL DEFAULT 'aluno'"))
        conn.commit()

_migrar_colunas_alunos()

# ─── Lifespan (scheduler) ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = criar_scheduler()
    scheduler.start()
    logger.info("Scheduler de alertas iniciado.")
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler encerrado.")

# ─── App FastAPI ──────────────────────────────────────────────────────────
app = FastAPI(
    title="RU — Sistema de Créditos",
    description="Gerenciamento de créditos do Restaurante Universitário",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

# ─── Middlewares ──────────────────────────────────────────────────────────
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=86400,   # 24h
)

# ─── Arquivos estáticos ───────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── Templates ───────────────────────────────────────────────────────────
templates = Jinja2Templates(directory="templates")

# ─── Routers ─────────────────────────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(aluno.router)
app.include_router(admin.router)
app.include_router(webhook.router)


# ─── Handler de erros 401/403 ────────────────────────────────────────────
@app.exception_handler(401)
async def nao_autenticado(request: Request, exc):
    if request.url.path.startswith("/admin"):
        return RedirectResponse(url="/admin/login", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.exception_handler(404)
async def nao_encontrado(request: Request, exc):
    return templates.TemplateResponse(request, "404.html", {}, status_code=404)


@app.exception_handler(429)
async def muitas_tentativas(request: Request, exc):
    from config import RATE_LIMIT_JANELA_MINUTOS
    return templates.TemplateResponse(
        request, "429.html",
        {"minutos": RATE_LIMIT_JANELA_MINUTOS},
        status_code=429,
    )
