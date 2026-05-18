"""
scheduler.py — Alertas automáticos de abertura e fechamento do RU.

Horários (horário de Brasília, seg–sex, exceto feriados):
  11:00 → RU abriu para o almoço  + cardápio do dia
  13:30 → RU fecha o almoço em 30 min
  19:00 → RU abriu para o jantar  + cardápio da noite
  20:30 → RU fecha o jantar em 30 min
"""
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import FERIADOS_NACIONAIS
from database import SessionLocal
from models import Aluno, Cardapio, TipoRefeicao
from email_service import enviar_emails_alerta_lote

logger = logging.getLogger(__name__)
BR_TZ = ZoneInfo("America/Sao_Paulo")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hoje_e_feriado() -> bool:
    return datetime.now(BR_TZ).date() in FERIADOS_NACIONAIS


def _get_emails() -> list[str]:
    db = SessionLocal()
    try:
        return [a.email for a in db.query(Aluno).filter(Aluno.ativo == True).all() if a.email]
    finally:
        db.close()


def _get_cardapio(tipo: TipoRefeicao) -> Cardapio | None:
    db = SessionLocal()
    try:
        hoje = datetime.now(BR_TZ).date()
        return db.query(Cardapio).filter(
            Cardapio.data == hoje,
            Cardapio.tipo == tipo,
        ).first()
    finally:
        db.close()


def _texto_cardapio(cardapio: Cardapio | None, refeicao: str) -> str:
    if not cardapio:
        return f"O cardápio do {refeicao} de hoje ainda não foi cadastrado."
    linhas = []
    if cardapio.prato_principal:
        linhas.append(f"🍽️ Prato principal: {cardapio.prato_principal}")
    if cardapio.acompanhamentos:
        linhas.append(f"🥗 Acompanhamentos: {cardapio.acompanhamentos}")
    if cardapio.sobremesa:
        linhas.append(f"🍮 Sobremesa: {cardapio.sobremesa}")
    if cardapio.observacao:
        linhas.append(f"ℹ️ {cardapio.observacao}")
    return "\n".join(linhas) if linhas else "Cardápio disponível no restaurante."


def _disparar(emails: list[str], assunto: str, mensagem: str):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, enviar_emails_alerta_lote, emails, assunto, mensagem)


# ── Jobs ──────────────────────────────────────────────────────────────────────

async def alerta_abertura_almoco():
    if _hoje_e_feriado():
        logger.info("Feriado — alerta almoço cancelado.")
        return
    cardapio = _get_cardapio(TipoRefeicao.almoco)
    menu = _texto_cardapio(cardapio, "almoço")
    mensagem = f"🍽️ O RU está aberto para o almoço!\n\n⏰ Horário: 11h às 14h\n\n{menu}"
    emails = _get_emails()
    _disparar(emails, "🍽️ RU aberto — Almoço", mensagem)
    logger.info("Alerta abertura almoço disparado para %d alunos.", len(emails))


async def alerta_fechamento_almoco():
    if _hoje_e_feriado():
        return
    mensagem = "⏰ O RU fecha para o almoço em 30 minutos (às 14h).\n\nSe ainda não almoçou, venha logo!"
    emails = _get_emails()
    _disparar(emails, "⏰ RU fecha em 30 min — Almoço", mensagem)
    logger.info("Alerta fechamento almoço disparado.")


async def alerta_abertura_jantar():
    if _hoje_e_feriado():
        logger.info("Feriado — alerta jantar cancelado.")
        return
    cardapio = _get_cardapio(TipoRefeicao.jantar)
    menu = _texto_cardapio(cardapio, "jantar")
    mensagem = f"🌙 O RU está aberto para o jantar!\n\n⏰ Horário: 19h às 21h\n\n{menu}"
    emails = _get_emails()
    _disparar(emails, "🌙 RU aberto — Jantar", mensagem)
    logger.info("Alerta abertura jantar disparado para %d alunos.", len(emails))


async def alerta_fechamento_jantar():
    if _hoje_e_feriado():
        return
    mensagem = "⏰ O RU fecha para o jantar em 30 minutos (às 21h).\n\nÚltima chance de jantar hoje!"
    emails = _get_emails()
    _disparar(emails, "⏰ RU fecha em 30 min — Jantar", mensagem)
    logger.info("Alerta fechamento jantar disparado.")


# ── Criação do scheduler ──────────────────────────────────────────────────────

def criar_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=BR_TZ)
    scheduler.add_job(
        alerta_abertura_almoco,
        CronTrigger(hour=11, minute=0, day_of_week="mon-fri", timezone=BR_TZ),
        id="abertura_almoco",
    )
    scheduler.add_job(
        alerta_fechamento_almoco,
        CronTrigger(hour=13, minute=30, day_of_week="mon-fri", timezone=BR_TZ),
        id="fechamento_almoco",
    )
    scheduler.add_job(
        alerta_abertura_jantar,
        CronTrigger(hour=19, minute=0, day_of_week="mon-fri", timezone=BR_TZ),
        id="abertura_jantar",
    )
    scheduler.add_job(
        alerta_fechamento_jantar,
        CronTrigger(hour=20, minute=30, day_of_week="mon-fri", timezone=BR_TZ),
        id="fechamento_jantar",
    )
    return scheduler
