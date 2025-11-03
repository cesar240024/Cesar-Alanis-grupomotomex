# databases/leads/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases.leads.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./leads.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Crear tablas
Base.metadata.create_all(bind=engine)
