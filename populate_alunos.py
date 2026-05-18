# -*- coding: utf-8 -*-
"""
populate_alunos.py
  1. Atualiza as matrículas dos alunos existentes para o padrão 20260XXX
  2. Insere 191 novos alunos aleatórios

Execute com: python populate_alunos.py
"""
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from database import engine, SessionLocal, Base
import models  # noqa
from models import Aluno, CategoriaAluno
from auth import hash_senha

Base.metadata.create_all(bind=engine)

NOMES_MASCULINOS = [
    "Gabriel","Lucas","Matheus","Pedro","Rafael","Henrique","Felipe","Gustavo","Bruno",
    "Carlos","Eduardo","Fernando","Marcos","André","Diego","Rodrigo","Thiago","Leonardo",
    "Alexandre","Victor","João","Arthur","Caio","Murilo","Igor","Vinícius","Leandro",
    "Renato","Danilo","Ricardo","Samuel","Patrick","Luiz","Daniel","Fábio","Marcelo",
    "Juliano","Claudio","Cristiano","Otávio","Sérgio","Márcio","Wellington","Renan",
    "Alan","César","Hudson","Erick","Nathan","Davi",
]

NOMES_FEMININOS = [
    "Ana","Beatriz","Camila","Carolina","Fernanda","Gabriela","Isabella","Júlia",
    "Larissa","Laura","Letícia","Luana","Mariana","Natália","Patrícia","Rafaela",
    "Renata","Sabrina","Thaís","Vanessa","Amanda","Bruna","Débora","Elisa","Giovana",
    "Helena","Isadora","Jéssica","Karla","Lívia","Milena","Nicole","Priscila","Roberta",
    "Sandra","Tatiane","Vitória","Yasmin","Alice","Aline","Bianca","Claudia","Diana",
    "Erika","Fabiana","Graziela","Ingrid","Joana","Kelly",
]

SOBRENOMES = [
    "Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Alves","Pereira",
    "Lima","Gomes","Costa","Ribeiro","Martins","Carvalho","Almeida","Lopes","Sousa",
    "Fernandes","Vieira","Barbosa","Rocha","Dias","Nascimento","Andrade","Moreira",
    "Nunes","Marques","Machado","Mendes","Freitas","Cardoso","Ramos","Gonçalves",
    "Correia","Teixeira","Araújo","Cavalcante","Pinto","Monteiro","Cruz","Fonseca",
    "Moraes","Cunha","Pires","Borges","Castro","Campos","Miranda","Azevedo","Guimarães",
    "Batista","Brito","Melo","Figueiredo","Xavier","Tavares","Lacerda","Porto","Leal",
]

DOMINIOS_EMAIL = [
    "ufcat.edu.br", "gmail.com", "hotmail.com", "outlook.com", "yahoo.com.br",
]

SENHA_PADRAO = "Aluno@2024"

CATEGORIAS_PESO = [
    (CategoriaAluno.aluno,      65),
    (CategoriaAluno.subsidiado, 20),
    (CategoriaAluno.bolsista,   10),
    (CategoriaAluno.externo,     5),
]

def _categoria_aleatoria():
    opcoes  = [c for c, _ in CATEGORIAS_PESO]
    pesos   = [p for _, p in CATEGORIAS_PESO]
    return random.choices(opcoes, weights=pesos, k=1)[0]

def _gerar_nome():
    feminino = random.random() < 0.5
    primeiro = random.choice(NOMES_FEMININOS if feminino else NOMES_MASCULINOS)
    meio     = random.choice(NOMES_FEMININOS + NOMES_MASCULINOS) if random.random() < 0.3 else None
    sobre1   = random.choice(SOBRENOMES)
    sobre2   = random.choice(SOBRENOMES)
    partes   = [primeiro] + ([meio] if meio else []) + [sobre1, sobre2]
    return " ".join(partes)

def _gerar_email(nome: str, matricula: str) -> str:
    partes = nome.lower().split()
    slug   = f"{partes[0]}.{partes[-1]}{random.randint(1, 99)}"
    slug   = slug.replace("á","a").replace("ã","a").replace("â","a") \
                 .replace("é","e").replace("ê","e").replace("í","i") \
                 .replace("ó","o").replace("õ","o").replace("ô","o") \
                 .replace("ú","u").replace("ç","c")
    dominio = random.choice(DOMINIOS_EMAIL)
    return f"{slug}@{dominio}"

def _creditos_aleatorios(categoria: CategoriaAluno) -> Decimal:
    if categoria == CategoriaAluno.bolsista:
        return Decimal("0.00")
    return Decimal(str(round(random.uniform(0, 80), 2)))

def _data_criacao_aleatoria() -> datetime:
    dias = random.randint(10, 730)
    return datetime.utcnow() - timedelta(days=dias)


def run():
    db = SessionLocal()
    try:
        # ── 1. Atualiza matrículas existentes ────────────────────────────────
        existentes = db.query(Aluno).order_by(Aluno.id).all()
        print(f"[INFO] {len(existentes)} alunos existentes encontrados. Atualizando matrículas...")

        for i, aluno in enumerate(existentes, start=1):
            nova_mat = f"20260{i:03d}"
            print(f"  {aluno.matricula} → {nova_mat}  ({aluno.nome})")
            aluno.matricula = nova_mat

        db.flush()
        proximo_seq = len(existentes) + 1

        # ── 2. Insere 191 novos alunos ────────────────────────────────────────
        emails_usados    = {a.email for a in existentes}
        matriculas_usadas = {a.matricula for a in existentes}

        novos = 0
        tentativas = 0
        senha_hash = hash_senha(SENHA_PADRAO)

        while novos < 191:
            tentativas += 1
            if tentativas > 5000:
                print("[AVISO] Limite de tentativas atingido.")
                break

            matricula = f"20260{proximo_seq:03d}"
            if matricula in matriculas_usadas:
                proximo_seq += 1
                continue

            nome  = _gerar_nome()
            email = _gerar_email(nome, matricula)
            if email in emails_usados:
                continue

            categoria = _categoria_aleatoria()
            creditos  = _creditos_aleatorios(categoria)

            aluno = Aluno(
                matricula      = matricula,
                nome           = nome,
                email          = email,
                senha_hash     = senha_hash,
                creditos       = creditos,
                categoria      = categoria,
                primeiro_acesso= False,
                ativo          = True,
                criado_em      = _data_criacao_aleatoria(),
            )
            db.add(aluno)
            emails_usados.add(email)
            matriculas_usadas.add(matricula)
            novos       += 1
            proximo_seq += 1

        db.commit()

        # ── Resumo ────────────────────────────────────────────────────────────
        total = db.query(Aluno).count()
        print(f"\n{'='*55}")
        print(f"[OK] {len(existentes)} matrículas atualizadas")
        print(f"[OK] {novos} novos alunos inseridos")
        print(f"[OK] Total de alunos no banco: {total}")
        print(f"     Matrículas: 20260001 → 20260{proximo_seq-1:03d}")
        print(f"     Senha padrão: {SENHA_PADRAO}")
        print(f"{'='*55}\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
