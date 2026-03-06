from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="operator")


class Credor(Base, TimestampMixin):
    __tablename__ = "credores"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    cnpj: Mapped[str] = mapped_column(String(18), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(9), nullable=True)
    titulos = relationship("Titulo", back_populates="credor")


class Devedor(Base, TimestampMixin):
    __tablename__ = "devedores"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    cpf_cnpj: Mapped[str] = mapped_column(String(18), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(9), nullable=True)
    perfil_risco: Mapped[str] = mapped_column(String(20), default="medio")
    titulos = relationship("Titulo", back_populates="devedor")


class Titulo(Base, TimestampMixin):
    __tablename__ = "titulos"
    id: Mapped[int] = mapped_column(primary_key=True)
    credor_id: Mapped[int] = mapped_column(ForeignKey("credores.id"))
    devedor_id: Mapped[int] = mapped_column(ForeignKey("devedores.id"))
    numero_documento: Mapped[str] = mapped_column(String(50), unique=True)
    valor_principal: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    data_emissao: Mapped[date] = mapped_column(Date)
    data_vencimento: Mapped[date] = mapped_column(Date)
    fase_cobranca: Mapped[str] = mapped_column(String(30), default="preventiva")
    status: Mapped[str] = mapped_column(String(30), default="em_aberto")

    credor = relationship("Credor", back_populates="titulos")
    devedor = relationship("Devedor", back_populates="titulos")
    recebimentos = relationship("Recebimento", back_populates="titulo")


class Recebimento(Base, TimestampMixin):
    __tablename__ = "recebimentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo_id: Mapped[int] = mapped_column(ForeignKey("titulos.id"))
    valor_pago: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    data_pagamento: Mapped[date] = mapped_column(Date)
    forma_pagamento: Mapped[str] = mapped_column(String(30))
    titulo = relationship("Titulo", back_populates="recebimentos")


class InteracaoCRM(Base, TimestampMixin):
    __tablename__ = "interacoes_crm"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo_id: Mapped[int] = mapped_column(ForeignKey("titulos.id"))
    canal: Mapped[str] = mapped_column(String(30))
    resumo: Mapped[str] = mapped_column(Text)
    proxima_acao: Mapped[str | None] = mapped_column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100))
    entity: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[int] = mapped_column()
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
