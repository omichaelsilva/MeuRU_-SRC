# -*- coding: utf-8 -*-
"""
seed.py -- Popula o banco de dados com dados iniciais para desenvolvimento.

Execute com: python seed.py
"""
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Força UTF-8 no terminal Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from database import engine, SessionLocal, Base
import models  # noqa: carrega todos os modelos
from models import Aluno, Admin, HistoricoRefeicao, HistoricoRecarga, RoleAdmin, TipoRefeicao, TipoRecarga
from auth import hash_senha

# Cria as tabelas
Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        # Verifica se ja foi seedado
        if db.query(Admin).count() > 0:
            print("[AVISO] Banco ja possui dados. Para re-seedar, delete ru.db e execute novamente.")
            return

        print("[SEED] Iniciando seed do banco de dados...\n")

        # --- Super Admin ---
        super_admin = Admin(
            nome="Administrador do RU",
            email="admin@ru.edu.br",
            senha_hash=hash_senha("Admin@2024"),
            role=RoleAdmin.super_admin,
            ativo=True,
            criado_em=datetime.utcnow()
        )
        db.add(super_admin)
        db.flush()  # Obtem o ID sem commitar
        print("[OK] Super Admin criado: admin@ru.edu.br / Admin@2024")

        # Admin operador adicional
        operador = Admin(
            nome="Maria Operadora",
            email="operador@ru.edu.br",
            senha_hash=hash_senha("Oper@2024"),
            role=RoleAdmin.operador,
            ativo=True,
            criado_por=super_admin.id,
            criado_em=datetime.utcnow()
        )
        db.add(operador)
        db.flush()
        print("[OK] Operador criado: operador@ru.edu.br / Oper@2024")

        # --- Alunos de teste ---
        alunos_data = [
            ("2024001", "Ana Silva Santos",      "ana.silva@uni.edu.br",     15.00, False),
            ("2024002", "Bruno Costa Oliveira",  "bruno.costa@uni.edu.br",    8.00, False),
            ("2024003", "Carla Mendes Ferreira", "carla.mendes@uni.edu.br",   0.00, False),
            ("2024004", "Daniel Rocha Lima",     "daniel.rocha@uni.edu.br",  22.50, True),   # primeiro acesso
            ("2024005", "Eduarda Pires Nunes",   "eduarda.pires@uni.edu.br",  5.00, False),
        ]

        alunos_criados = []
        for matricula, nome, email, creditos, primeiro_acesso in alunos_data:
            aluno = Aluno(
                matricula=matricula,
                nome=nome,
                email=email,
                senha_hash=hash_senha("Aluno@2024") if not primeiro_acesso else hash_senha("senha_temp"),
                creditos=Decimal(str(creditos)),
                primeiro_acesso=primeiro_acesso,
                ativo=True,
                criado_em=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            db.add(aluno)
            alunos_criados.append(aluno)

        db.flush()
        print(f"[OK] {len(alunos_criados)} alunos criados:")
        for a in alunos_criados:
            status = " (primeiro acesso)" if a.primeiro_acesso else ""
            print(f"   - Matricula {a.matricula}: {a.nome}{status} | R$ {float(a.creditos):.2f}")

        # --- Historico de recargas (ultimos 30 dias) ---
        recargas_criadas = 0
        for aluno in alunos_criados:
            num_recargas = random.randint(1, 4)
            for i in range(num_recargas):
                dias_atras = random.randint(1, 30)
                valor = random.choice([5.00, 10.00, 15.00, 20.00, 30.00, 50.00])
                recarga = HistoricoRecarga(
                    aluno_id=aluno.id,
                    admin_id=super_admin.id,
                    tipo=TipoRecarga.recarga,
                    valor=Decimal(str(valor)),
                    observacao=random.choice([
                        "Recarga mensal", "Recarga solicitada pelo aluno",
                        "Recarga via caixa", None
                    ]),
                    data_hora=datetime.utcnow() - timedelta(
                        days=dias_atras,
                        hours=random.randint(8, 17),
                        minutes=random.randint(0, 59)
                    )
                )
                db.add(recarga)
                recargas_criadas += 1

        print(f"[OK] {recargas_criadas} recargas historicas criadas")

        # --- Historico de refeicoes (ultimos 30 dias) ---
        refeicoes_criadas = 0
        horarios_almoco = [(11, 30), (12, 0), (12, 30), (13, 0)]
        horarios_jantar = [(18, 0), (18, 30), (19, 0), (19, 30)]

        for aluno in alunos_criados[:3]:  # Apenas 3 alunos tem historico
            for dia_offset in range(30):
                data = datetime.utcnow() - timedelta(days=dia_offset)
                # Pula fins de semana com 70% de chance
                if data.weekday() >= 5 and random.random() < 0.7:
                    continue

                # Almoco: ~80% de chance
                if random.random() < 0.80:
                    hora, minuto = random.choice(horarios_almoco)
                    refeicao = HistoricoRefeicao(
                        aluno_id=aluno.id,
                        tipo=TipoRefeicao.almoco,
                        creditos_utilizados=Decimal("1.50"),
                        data_hora=data.replace(hour=hora, minute=minuto, second=0),
                        registrado_por=None  # autoatendimento
                    )
                    db.add(refeicao)
                    refeicoes_criadas += 1

                # Jantar: ~30% de chance
                if random.random() < 0.30:
                    hora, minuto = random.choice(horarios_jantar)
                    refeicao = HistoricoRefeicao(
                        aluno_id=aluno.id,
                        tipo=TipoRefeicao.jantar,
                        creditos_utilizados=Decimal("1.50"),
                        data_hora=data.replace(hour=hora, minute=minuto, second=0),
                        registrado_por=None
                    )
                    db.add(refeicao)
                    refeicoes_criadas += 1

        print(f"[OK] {refeicoes_criadas} refeicoes historicas criadas (ultimos 30 dias)")

        db.commit()
        print("\n" + "="*55)
        print("[SEED] Concluido com sucesso!")
        print("="*55)
        print("\nCREDENCIAIS DE ACESSO:")
        print("\nALUNOS (senha: Aluno@2024):")
        for a in alunos_criados:
            if not a.primeiro_acesso:
                print(f"   Matricula: {a.matricula}  |  {a.nome}")
        print("\nADMIN:")
        print("   admin@ru.edu.br      /  Admin@2024  (super_admin)")
        print("   operador@ru.edu.br   /  Oper@2024   (operador)")
        print("\nURLs:")
        print("   Aluno: http://localhost:8000/login")
        print("   Admin: http://localhost:8000/admin/login")
        print("="*55 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] Erro durante o seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
