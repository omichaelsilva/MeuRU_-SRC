"""
Configuração do banco de dados com SQLAlchemy.
Padrão: SQLite (zero configuração, arquivo local ru.db)

Para migrar para PostgreSQL:
1. Instale: pip install psycopg2-binary
2. No .env, defina: DATABASE_URL=postgresql://usuario:senha@localhost:5432/ru_db
3. Remova o argumento connect_args abaixo (específico do SQLite)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# SQLite requer check_same_thread=False para uso com FastAPI (multithread)
# PostgreSQL não precisa desse argumento — remova connect_args para outros bancos
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # Para PostgreSQL, adicione: pool_size=10, max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: fornece sessão de banco e garante fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
