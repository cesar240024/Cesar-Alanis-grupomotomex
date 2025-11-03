# databases/leads/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    canal = Column(String, nullable=True)
    mensaje = Column(String, nullable=False)
    tipo_cliente = Column(String, nullable=True)
    segmento = Column(String, nullable=True)
    urgencia = Column(String, nullable=True)
    ticket = Column(Float, nullable=True)
    ponderacion_total = Column(Float, nullable=True)
    score_final = Column(Float, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
