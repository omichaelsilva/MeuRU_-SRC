"""
Rotas da área do aluno: dashboard, histórico e exportação CSV.
"""
import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Request, Depends, Query, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from database import get_db
from models import Aluno, HistoricoRefeicao, HistoricoRecarga, TipoRefeicao, TipoRecarga
from auth import obter_aluno_atual, gerar_csrf_token, verificar_csrf
from whatsapp_bot import obter_status_pico
from config import PRECOS_REFEICAO

router = APIRouter(prefix="/aluno")
templates = Jinja2Templates(directory="templates")

ITENS_POR_PAGINA = 20


def _get_aluno(payload: dict, db: Session) -> Aluno:
    aluno = db.query(Aluno).filter(
        Aluno.id == int(payload["sub"]),
        Aluno.ativo == True
    ).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


# ─── Dashboard ─────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        payload = obter_aluno_atual(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    aluno = _get_aluno(payload, db)

    agora = datetime.utcnow()
    refeicoes_mes = db.query(HistoricoRefeicao).filter(
        HistoricoRefeicao.aluno_id == aluno.id,
        extract("month", HistoricoRefeicao.data_hora) == agora.month,
        extract("year", HistoricoRefeicao.data_hora) == agora.year
    ).count()

    from collections import defaultdict
    ultimas_refeicoes = db.query(HistoricoRefeicao).filter(
        HistoricoRefeicao.aluno_id == aluno.id
    ).order_by(HistoricoRefeicao.data_hora.desc()).limit(100).all()

    semanas: dict = defaultdict(int)
    for r in ultimas_refeicoes:
        semana = r.data_hora.strftime("%Y-W%W")
        semanas[semana] += 1

    semanas_ordenadas = sorted(semanas.items())[-8:]
    labels_semanas = [s[0] for s in semanas_ordenadas]
    dados_semanas = [s[1] for s in semanas_ordenadas]

    ultimas_5 = db.query(HistoricoRefeicao).filter(
        HistoricoRefeicao.aluno_id == aluno.id
    ).order_by(HistoricoRefeicao.data_hora.desc()).limit(5).all()

    custo_refeicao = PRECOS_REFEICAO.get(aluno.categoria.value, Decimal("6.00"))

    csrf = gerar_csrf_token()
    resposta = templates.TemplateResponse(request, "aluno/dashboard.html", {
        "aluno": aluno,
        "refeicoes_mes": refeicoes_mes,
        "labels_semanas": labels_semanas,
        "dados_semanas": dados_semanas,
        "ultimas_refeicoes": ultimas_5,
        "creditos_formatado": f"{float(aluno.creditos):.2f}".replace(".", ","),
        "custo_refeicao": f"{float(custo_refeicao):.2f}".replace(".", ","),
        "csrf_token": csrf,
        "status_pico": obter_status_pico(db),
    })
    resposta.set_cookie("csrf_token", csrf, httponly=False, samesite="lax")
    return resposta


# ─── Histórico ─────────────────────────────────────────────────────────────

@router.get("/historico", response_class=HTMLResponse)
async def historico(
    request: Request,
    pagina: int = Query(1, ge=1),
    tipo: str = Query("todos"),
    data_inicio: str = Query(""),
    data_fim: str = Query(""),
    exportar: str = Query(""),
    db: Session = Depends(get_db)
):
    try:
        payload = obter_aluno_atual(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    aluno = _get_aluno(payload, db)

    query = db.query(HistoricoRefeicao).filter(
        HistoricoRefeicao.aluno_id == aluno.id
    )

    if tipo == "almoco":
        query = query.filter(HistoricoRefeicao.tipo == TipoRefeicao.almoco)
    elif tipo == "jantar":
        query = query.filter(HistoricoRefeicao.tipo == TipoRefeicao.jantar)

    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(HistoricoRefeicao.data_hora >= dt_inicio)
        except ValueError:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(HistoricoRefeicao.data_hora <= dt_fim)
        except ValueError:
            pass

    query = query.order_by(HistoricoRefeicao.data_hora.desc())

    if exportar == "csv":
        registros = query.all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Data/Hora", "Tipo", "Créditos Utilizados"])
        for r in registros:
            writer.writerow([
                r.data_hora.strftime("%d/%m/%Y %H:%M"),
                "Almoço" if r.tipo == TipoRefeicao.almoco else "Jantar",
                f"R$ {float(r.creditos_utilizados):.2f}".replace(".", ",")
            ])
        output.seek(0)
        nome_arquivo = f"historico_refeicoes_{aluno.matricula}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )

    total = query.count()
    total_paginas = max(1, (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * ITENS_POR_PAGINA
    registros = query.offset(offset).limit(ITENS_POR_PAGINA).all()

    csrf = gerar_csrf_token()
    resposta = templates.TemplateResponse(request, "aluno/historico.html", {
        "aluno": aluno,
        "registros": registros,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "total": total,
        "tipo": tipo,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "itens_por_pagina": ITENS_POR_PAGINA,
        "csrf_token": csrf,
    })
    resposta.set_cookie("csrf_token", csrf, httponly=False, samesite="lax")
    return resposta


# ─── Recarga pelo aluno ────────────────────────────────────────────────────

@router.post("/recarregar")
async def recarregar_post(
    request: Request,
    valor: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        payload = obter_aluno_atual(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    verificar_csrf(request, {"csrf_token": csrf_token})

    aluno = db.query(Aluno).filter(
        Aluno.id == int(payload["sub"]),
        Aluno.ativo == True
    ).first()
    if not aluno:
        return RedirectResponse(url="/login", status_code=302)

    try:
        valor_decimal = Decimal(valor.replace(",", "."))
        if valor_decimal <= 0 or valor_decimal > 500:
            raise ValueError
    except (InvalidOperation, ValueError):
        return RedirectResponse(url="/aluno/dashboard?erro=valor_invalido", status_code=303)

    aluno.creditos = Decimal(str(aluno.creditos)) + valor_decimal

    recarga = HistoricoRecarga(
        aluno_id=aluno.id,
        admin_id=None,
        tipo=TipoRecarga.recarga,
        valor=valor_decimal,
        observacao="Recarga realizada pelo aluno",
    )
    db.add(recarga)
    db.commit()

    return RedirectResponse(url="/aluno/dashboard?msg=recarga_ok", status_code=303)


# ─── Registrar Refeição pelo aluno ────────────────────────────────────────────

@router.post("/registrar-refeicao")
async def registrar_refeicao_post(
    request: Request,
    tipo: str = Form("almoco"),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        payload = obter_aluno_atual(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)

    verificar_csrf(request, {"csrf_token": csrf_token})

    aluno = db.query(Aluno).filter(
        Aluno.id == int(payload["sub"]),
        Aluno.ativo == True
    ).first()
    if not aluno:
        return RedirectResponse(url="/login", status_code=302)

    try:
        tipo_enum = TipoRefeicao(tipo)
    except ValueError:
        tipo_enum = TipoRefeicao.almoco

    custo = PRECOS_REFEICAO.get(aluno.categoria.value, Decimal("6.00"))
    if custo > 0 and Decimal(str(aluno.creditos)) < custo:
        return RedirectResponse(url="/aluno/dashboard?erro=saldo_insuficiente", status_code=303)

    if custo > 0:
        aluno.creditos = Decimal(str(aluno.creditos)) - custo

    refeicao = HistoricoRefeicao(
        aluno_id=aluno.id,
        tipo=tipo_enum,
        creditos_utilizados=custo,
        data_hora=datetime.utcnow(),
        registrado_por=None,
    )
    db.add(refeicao)
    db.commit()

    return RedirectResponse(url="/aluno/dashboard?msg=refeicao_ok", status_code=303)
