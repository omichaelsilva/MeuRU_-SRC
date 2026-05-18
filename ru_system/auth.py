"""
Módulo de autenticação: JWT, bcrypt, rate limiting e CSRF.
"""
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
import bcrypt

from config import (
    SECRET_KEY, ALGORITHM,
    EXPIRACAO_TOKEN_ALUNO_HORAS, EXPIRACAO_TOKEN_ADMIN_HORAS,
    RATE_LIMIT_MAX_TENTATIVAS, RATE_LIMIT_JANELA_MINUTOS
)

# ─── Bcrypt ──────────────────────────────────────────────────────────────────
# Usa bcrypt diretamente (compatível com bcrypt >= 4.0)

def hash_senha(senha: str) -> str:
    """Gera hash bcrypt da senha (salt rounds: 12)."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verificar_senha(senha: str, hash: str) -> bool:
    """Verifica se a senha corresponde ao hash bcrypt."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), hash.encode("utf-8"))
    except Exception:
        return False


# ─── JWT ─────────────────────────────────────────────────────────────────────

def criar_token_jwt(dados: dict, horas: int) -> str:
    """Cria um token JWT com os dados fornecidos e tempo de expiração."""
    payload = dados.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=horas)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def criar_token_aluno(aluno_id: int, matricula: str) -> str:
    return criar_token_jwt(
        {"sub": str(aluno_id), "matricula": matricula, "tipo": "aluno"},
        EXPIRACAO_TOKEN_ALUNO_HORAS
    )


def criar_token_admin(admin_id: int, email: str, role: str) -> str:
    return criar_token_jwt(
        {"sub": str(admin_id), "email": email, "role": role, "tipo": "admin"},
        EXPIRACAO_TOKEN_ADMIN_HORAS
    )


def decodificar_token(token: str) -> dict:
    """Decodifica e valida um token JWT. Lança HTTPException se inválido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


# ─── Dependencies FastAPI ─────────────────────────────────────────────────────

def obter_aluno_atual(request: Request):
    """
    Dependency: extrai e valida o token do aluno do cookie.
    Retorna o payload do JWT ou redireciona para login.
    """
    token = request.cookies.get("aluno_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    payload = decodificar_token(token)
    if payload.get("tipo") != "aluno":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    return payload


def obter_admin_atual(request: Request):
    """
    Dependency: extrai e valida o token do admin do cookie.
    Retorna o payload do JWT.
    """
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    payload = decodificar_token(token)
    if payload.get("tipo") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    return payload


def exigir_super_admin(payload: dict):
    """Verifica se o admin tem role super_admin. Lança 403 caso contrário."""
    if payload.get("role") != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas super_admin pode realizar esta ação"
        )


# ─── Rate Limiting ────────────────────────────────────────────────────────────

# Estrutura: {ip: [timestamp, timestamp, ...]}
_tentativas_login: dict = defaultdict(list)


def verificar_rate_limit(ip: str):
    """
    Verifica se o IP excedeu o limite de tentativas de login.
    Lança HTTPException 429 se bloqueado.
    """
    agora = datetime.utcnow()
    janela = timedelta(minutes=RATE_LIMIT_JANELA_MINUTOS)

    # Remove tentativas fora da janela de tempo
    _tentativas_login[ip] = [
        t for t in _tentativas_login[ip]
        if agora - t < janela
    ]

    if len(_tentativas_login[ip]) >= RATE_LIMIT_MAX_TENTATIVAS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Tente novamente em {RATE_LIMIT_JANELA_MINUTOS} minutos."
        )


def registrar_tentativa_login(ip: str):
    """Registra uma tentativa de login falha para o IP."""
    _tentativas_login[ip].append(datetime.utcnow())


def limpar_tentativas_login(ip: str):
    """Limpa tentativas após login bem-sucedido."""
    _tentativas_login.pop(ip, None)


# ─── CSRF ─────────────────────────────────────────────────────────────────────

import secrets


def gerar_csrf_token() -> str:
    """Gera um token CSRF aleatório."""
    return secrets.token_hex(32)


def verificar_csrf(request: Request, form_data: dict):
    """
    Verifica token CSRF: compara o token do cookie com o do formulário.
    Lança HTTPException 403 se inválido.
    """
    token_cookie = request.cookies.get("csrf_token")
    token_form = form_data.get("csrf_token")

    if not token_cookie or not token_form:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF ausente"
        )
    if not secrets.compare_digest(token_cookie, token_form):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF inválido"
        )
