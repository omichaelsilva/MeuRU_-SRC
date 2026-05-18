"""
Schemas Pydantic para validação de entrada e saída de dados.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from models import RoleAdmin, TipoRefeicao, TipoRecarga


# ─── Autenticação ────────────────────────────────────────────────────────────

class LoginAluno(BaseModel):
    matricula: str
    senha: str


class LoginAdmin(BaseModel):
    email: str
    senha: str


class PrimeiroAcesso(BaseModel):
    matricula: str
    nova_senha: str
    confirmar_senha: str

    @field_validator("nova_senha")
    @classmethod
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos 1 letra maiúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos 1 número")
        return v


class RecuperarSenha(BaseModel):
    email: str


class RedefinirSenha(BaseModel):
    token: str
    nova_senha: str
    confirmar_senha: str

    @field_validator("nova_senha")
    @classmethod
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos 1 letra maiúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos 1 número")
        return v


# ─── Aluno ───────────────────────────────────────────────────────────────────

class AlunoOut(BaseModel):
    id: int
    matricula: str
    nome: str
    email: str
    creditos: Decimal
    primeiro_acesso: bool
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class AlunoResumo(BaseModel):
    id: int
    matricula: str
    nome: str
    email: str
    creditos: Decimal
    ativo: bool

    model_config = {"from_attributes": True}


# ─── Admin ───────────────────────────────────────────────────────────────────

class AdminOut(BaseModel):
    id: int
    nome: str
    email: str
    role: RoleAdmin
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class CriarAdmin(BaseModel):
    nome: str
    email: str
    senha: str
    role: RoleAdmin = RoleAdmin.operador

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        return v


# ─── Histórico de Refeições ──────────────────────────────────────────────────

class RefeicaoOut(BaseModel):
    id: int
    aluno_id: int
    tipo: TipoRefeicao
    creditos_utilizados: Decimal
    data_hora: datetime
    registrado_por: Optional[int]

    model_config = {"from_attributes": True}


class RefeicaoComAluno(BaseModel):
    id: int
    aluno_id: int
    aluno_nome: str
    aluno_matricula: str
    tipo: TipoRefeicao
    creditos_utilizados: Decimal
    data_hora: datetime

    model_config = {"from_attributes": True}


# ─── Histórico de Recargas ───────────────────────────────────────────────────

class RecargaOut(BaseModel):
    id: int
    aluno_id: int
    admin_id: int
    tipo: TipoRecarga
    valor: Decimal
    observacao: Optional[str]
    data_hora: datetime

    model_config = {"from_attributes": True}


class RecarregarCreditos(BaseModel):
    valor: Decimal
    observacao: Optional[str] = None

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v):
        if v <= 0:
            raise ValueError("Valor deve ser positivo")
        if v > 9999.99:
            raise ValueError("Valor máximo é R$ 9.999,99")
        return v


class RemoverCreditos(BaseModel):
    valor: Decimal
    observacao: str  # obrigatório para remoção

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v):
        if v <= 0:
            raise ValueError("Valor deve ser positivo")
        return v

    @field_validator("observacao")
    @classmethod
    def validar_observacao(cls, v):
        if not v or not v.strip():
            raise ValueError("Observação é obrigatória para remoção de créditos")
        return v.strip()


# ─── Paginação ───────────────────────────────────────────────────────────────

class Paginacao(BaseModel):
    pagina: int
    total_paginas: int
    total_itens: int
    itens_por_pagina: int
