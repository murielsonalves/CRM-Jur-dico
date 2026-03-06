from datetime import date
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class CredorBase(BaseModel):
    nome: str
    cnpj: str
    telefone: str | None = None
    email: EmailStr | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None


class DevedorBase(BaseModel):
    nome: str
    cpf_cnpj: str
    telefone: str | None = None
    email: EmailStr | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    perfil_risco: str = "medio"


class TituloBase(BaseModel):
    credor_id: int
    devedor_id: int
    numero_documento: str
    valor_principal: Decimal
    data_emissao: date
    data_vencimento: date
    fase_cobranca: str = "preventiva"
    status: str = "em_aberto"


class RecebimentoCreate(BaseModel):
    titulo_id: int
    valor_pago: Decimal
    data_pagamento: date
    forma_pagamento: str


class SimulationRequest(BaseModel):
    titulo_id: int


class AuthRequest(BaseModel):
    email: EmailStr
    password: str
