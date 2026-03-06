# Código completo consolidado

Este arquivo consolida **todos os códigos do projeto** em um único lugar.

## .gitignore

```
__pycache__/
*.pyc
.venv/
node_modules/
crm_juridico.db

```

## README.md

```
# CRM Jurídico de Cobrança

Sistema SaaS para escritórios de advocacia focado em recuperação de crédito, substituindo planilhas por automação ponta a ponta.

## Funcionalidades
- Gestão de credores, devedores e títulos
- Motor de cálculo de dívida com `Decimal`
- Simulador de acordos (3, 6, 9 e 12 parcelas)
- Registro de recebimentos e interações de CRM
- Geração automática de notificação, acordo e petição inicial
- API REST com FastAPI + SQLAlchemy

## Executar backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

## Estrutura
```text
app/
  api/ core/ models/ schemas/ repositories/ services/
  calculations/ tasks/ reports/ imports/ templates/
frontend/
```

```

## app/api/routes.py

```
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.crud import (
    CredorRepository,
    DevedorRepository,
    TituloRepository,
    RecebimentoRepository,
    InteracaoRepository,
    UserRepository,
)
from app.schemas.common import CredorBase, DevedorBase, TituloBase, RecebimentoCreate, SimulationRequest, AuthRequest
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.document_service import DocumentService
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/auth/register")
def register(payload: AuthRequest, db: Session = Depends(get_db)):
    service = AuthService(UserRepository(db))
    user = service.register(payload.email, payload.password, payload.email)
    return {"id": user.id, "email": user.email}


@router.post("/auth/login")
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    service = AuthService(UserRepository(db))
    token = service.login(payload.email, payload.password)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/credores")
def create_credor(payload: CredorBase, db: Session = Depends(get_db)):
    return CredorRepository(db).create(payload.model_dump())


@router.get("/credores")
def list_credores(db: Session = Depends(get_db)):
    return CredorRepository(db).list()


@router.post("/devedores")
def create_devedor(payload: DevedorBase, db: Session = Depends(get_db)):
    return DevedorRepository(db).create(payload.model_dump())


@router.get("/devedores")
def list_devedores(db: Session = Depends(get_db)):
    return DevedorRepository(db).list()


@router.post("/titulos")
def create_titulo(payload: TituloBase, db: Session = Depends(get_db)):
    return TituloRepository(db).create(payload.model_dump())


@router.get("/titulos")
def list_titulos(db: Session = Depends(get_db)):
    return TituloRepository(db).list()


@router.post("/recebimentos")
def create_recebimento(payload: RecebimentoCreate, db: Session = Depends(get_db)):
    return RecebimentoRepository(db).create(payload.model_dump())


@router.post("/crm/interacoes")
def create_interacao(payload: dict, db: Session = Depends(get_db)):
    return InteracaoRepository(db).create(payload)


@router.post("/acordos/simular")
def simular_acordo(payload: SimulationRequest, db: Session = Depends(get_db)):
    service = BillingService(TituloRepository(db))
    return service.simulador_acordo(payload.titulo_id)


@router.get("/titulos/{titulo_id}/saldo")
def saldo_titulo(titulo_id: int, db: Session = Depends(get_db)):
    service = BillingService(TituloRepository(db))
    return service.saldo_atualizado(titulo_id).__dict__


@router.get("/relatorios/carteira")
def relatorio_carteira(db: Session = Depends(get_db)):
    return ReportService(TituloRepository(db)).portfolio_summary()


@router.post("/documentos/{tipo}")
def gerar_documento(tipo: str, payload: dict):
    service = DocumentService()
    builders = {
        "notificacao": service.render_notificacao,
        "acordo": service.render_acordo,
        "peticao": service.render_peticao_inicial,
    }
    if tipo not in builders:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return {"conteudo": builders[tipo](payload)}

```

## app/calculations/debt_calculator.py

```
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class DebtBreakdown:
    principal: Decimal
    correcao: Decimal
    juros: Decimal
    multa: Decimal
    honorarios: Decimal
    despesas: Decimal
    custas: Decimal
    total: Decimal


class DebtCalculator:
    def __init__(self, monthly_interest: Decimal = Decimal("0.01"), multa_rate: Decimal = Decimal("0.02")):
        self.monthly_interest = monthly_interest
        self.multa_rate = multa_rate

    def calculate(self, principal: Decimal, due_date: date, reference_date: date) -> DebtBreakdown:
        days_overdue = max((reference_date - due_date).days, 0)
        months = Decimal(days_overdue) / Decimal(30)
        correcao = (principal * Decimal("0.003") * months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        juros = (principal * self.monthly_interest * months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        multa = (principal * self.multa_rate if days_overdue > 0 else Decimal("0")).quantize(Decimal("0.01"))
        base = principal + correcao + juros + multa
        honorarios = (base * Decimal("0.1")).quantize(Decimal("0.01"))
        despesas = Decimal("25.00")
        custas = Decimal("0.00")
        total = principal + correcao + juros + multa + honorarios + despesas + custas
        return DebtBreakdown(principal, correcao, juros, multa, honorarios, despesas, custas, total.quantize(Decimal("0.01")))


def build_installment_options(total: Decimal) -> dict[int, Decimal]:
    return {n: (total / Decimal(n)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) for n in (3, 6, 9, 12)}

```

## app/core/config.py

```
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CRM Jurídico de Cobrança"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./crm_juridico.db"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()

```

## app/core/database.py

```
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

## app/core/security.py

```
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

```

## app/imports/csv_importer.py

```
import csv


def read_titles_csv(path: str):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

```

## app/main.py

```
from fastapi import FastAPI

from app.api.routes import router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM Jurídico de Cobrança")
app.include_router(router, prefix="/api")


@app.get("/health")
def healthcheck():
    return {"status": "ok"}

```

## app/models/entities.py

```
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

```

## app/reports/README.md

```
# Relatórios

Este módulo consolida relatórios financeiros como aging da carteira, recebimentos e acordos.

```

## app/repositories/base.py

```
from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

```

## app/repositories/crud.py

```
from sqlalchemy import select

from app.models.entities import Credor, Devedor, Titulo, Recebimento, InteracaoCRM, User
from app.repositories.base import BaseRepository


class CredorRepository(BaseRepository):
    def create(self, data: dict) -> Credor:
        item = Credor(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self):
        return self.db.scalars(select(Credor).where(Credor.is_deleted.is_(False))).all()


class DevedorRepository(BaseRepository):
    def create(self, data: dict) -> Devedor:
        item = Devedor(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self):
        return self.db.scalars(select(Devedor).where(Devedor.is_deleted.is_(False))).all()


class TituloRepository(BaseRepository):
    def create(self, data: dict) -> Titulo:
        item = Titulo(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, titulo_id: int):
        return self.db.get(Titulo, titulo_id)

    def list(self):
        return self.db.scalars(select(Titulo).where(Titulo.is_deleted.is_(False))).all()


class RecebimentoRepository(BaseRepository):
    def create(self, data: dict) -> Recebimento:
        item = Recebimento(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item


class InteracaoRepository(BaseRepository):
    def create(self, data: dict) -> InteracaoCRM:
        item = InteracaoCRM(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item


class UserRepository(BaseRepository):
    def create(self, data: dict) -> User:
        item = User(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_email(self, email: str):
        return self.db.scalar(select(User).where(User.email == email, User.is_deleted.is_(False)))

```

## app/schemas/common.py

```
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

```

## app/services/auth_service.py

```
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.crud import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, email: str, password: str, full_name: str):
        return self.user_repo.create(
            {
                "email": email,
                "password_hash": hash_password(password),
                "full_name": full_name,
                "role": "admin",
            }
        )

    def login(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return create_access_token(user.email)

```

## app/services/billing_service.py

```
from datetime import date

from app.calculations.debt_calculator import DebtCalculator, build_installment_options
from app.repositories.crud import TituloRepository


class BillingService:
    def __init__(self, titulo_repo: TituloRepository):
        self.titulo_repo = titulo_repo
        self.calculator = DebtCalculator()

    def saldo_atualizado(self, titulo_id: int):
        titulo = self.titulo_repo.get(titulo_id)
        breakdown = self.calculator.calculate(titulo.valor_principal, titulo.data_vencimento, date.today())
        return breakdown

    def simulador_acordo(self, titulo_id: int):
        breakdown = self.saldo_atualizado(titulo_id)
        return build_installment_options(breakdown.total)

```

## app/services/document_service.py

```
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(BASE_DIR / "templates"))


class DocumentService:
    def render_notificacao(self, payload: dict) -> str:
        return env.get_template("notificacao_extrajudicial.j2").render(**payload, data=date.today())

    def render_acordo(self, payload: dict) -> str:
        return env.get_template("acordo.j2").render(**payload, data=date.today())

    def render_peticao_inicial(self, payload: dict) -> str:
        return env.get_template("peticao_inicial.j2").render(**payload, data=date.today())

```

## app/services/report_service.py

```
from decimal import Decimal

from app.repositories.crud import TituloRepository


class ReportService:
    def __init__(self, titulo_repo: TituloRepository):
        self.titulo_repo = titulo_repo

    def portfolio_summary(self):
        titulos = self.titulo_repo.list()
        total = sum((t.valor_principal for t in titulos), Decimal("0"))
        em_aberto = [t for t in titulos if t.status == "em_aberto"]
        return {
            "quantidade_titulos": len(titulos),
            "valor_total_carteira": str(total),
            "valor_em_aberto": str(sum((t.valor_principal for t in em_aberto), Decimal("0"))),
        }

```

## app/tasks/celery_app.py

```
from celery import Celery

from app.core.config import settings

celery = Celery("crm_juridico", broker=settings.redis_url, backend=settings.redis_url)


@celery.task
def enviar_cobranca_async(titulo_id: int, canal: str):
    return {"titulo_id": titulo_id, "canal": canal, "status": "agendado"}

```

## app/templates/acordo.j2

```
TERMO DE ACORDO

Credor: {{ credor_nome }}
Devedor: {{ devedor_nome }}
Valor negociado: R$ {{ valor_total }}
Parcelas: {{ parcelas }}x de R$ {{ valor_parcela }}

Firmado em {{ data }}.

```

## app/templates/notificacao_extrajudicial.j2

```
NOTIFICAÇÃO EXTRAJUDICIAL

Credor: {{ credor_nome }}
Devedor: {{ devedor_nome }}
Documento: {{ numero_documento }}
Valor atualizado: R$ {{ valor_total }}

Fica V.Sa. notificado para pagamento em 5 dias a contar de {{ data }}.

```

## app/templates/peticao_inicial.j2

```
PETIÇÃO INICIAL - AÇÃO DE COBRANÇA

Exequente: {{ credor_nome }}
Executado: {{ devedor_nome }}
Título: {{ numero_documento }}
Valor da causa: R$ {{ valor_total }}

Nestes termos, pede deferimento.
{{ data }}

```

## frontend/index.html

```
<!DOCTYPE html>
<html lang="pt-BR">
  <head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>CRM Jurídico</title></head>
  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>

```

## frontend/package.json

```
{
  "name": "crm-juridico-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build"
  },
  "dependencies": {
    "@mui/icons-material": "^5.15.14",
    "@mui/material": "^5.15.14",
    "axios": "^1.6.8",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.12.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "typescript": "^5.4.3",
    "vite": "^5.2.0"
  }
}

```

## frontend/src/App.tsx

```
import { AppLayout } from "./layout/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";

export function App() {
  return (
    <AppLayout>
      <DashboardPage />
    </AppLayout>
  );
}

```

## frontend/src/components/DashboardCard.tsx

```
import { Card, CardContent, Typography } from "@mui/material";

type Props = { label: string; value: string };

export function DashboardCard({ label, value }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="h5">{value}</Typography>
      </CardContent>
    </Card>
  );
}

```

## frontend/src/layout/AppLayout.tsx

```
import { Box, Drawer, List, ListItemButton, ListItemText, Toolbar, AppBar, Typography } from "@mui/material";
import { ReactNode } from "react";

const menu = ["Dashboard", "Credores", "Devedores", "Títulos", "Cobrança", "Acordos", "Recebimentos", "Relatórios", "Configurações"];

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <Box sx={{ display: "flex" }}>
      <AppBar position="fixed"><Toolbar><Typography>CRM Jurídico de Cobrança</Typography></Toolbar></AppBar>
      <Drawer variant="permanent" sx={{ width: 220, [`& .MuiDrawer-paper`]: { width: 220, marginTop: "64px" } }}>
        <List>{menu.map((m) => <ListItemButton key={m}><ListItemText primary={m} /></ListItemButton>)}</List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, marginTop: "64px", marginLeft: "220px" }}>{children}</Box>
    </Box>
  );
}

```

## frontend/src/main.tsx

```
import React from "react";
import ReactDOM from "react-dom/client";
import { CssBaseline } from "@mui/material";
import { App } from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <CssBaseline />
    <App />
  </React.StrictMode>,
);

```

## frontend/src/pages/DashboardPage.tsx

```
import { Grid, Typography } from "@mui/material";
import { DashboardCard } from "../components/DashboardCard";

export function DashboardPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>Dashboard Financeiro</Typography>
      <Grid container spacing={2}>
        <Grid item xs={3}><DashboardCard label="Carteira Total" value="R$ 4.250.000,00" /></Grid>
        <Grid item xs={3}><DashboardCard label="Valor Recuperado" value="R$ 1.730.000,00" /></Grid>
        <Grid item xs={3}><DashboardCard label="Em Aberto" value="R$ 2.520.000,00" /></Grid>
        <Grid item xs={3}><DashboardCard label="Taxa de Recuperação" value="40,7%" /></Grid>
      </Grid>
    </>
  );
}

```

## frontend/src/services/api.ts

```
import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

```

## frontend/tsconfig.json

```
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "jsx": "react-jsx",
    "strict": true,
    "moduleResolution": "Bundler",
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}

```

## pyproject.toml

```
[project]
name = "crm-juridico-cobranca"
version = "0.1.0"
description = "CRM jurídico para cobrança e recuperação de crédito"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
  "sqlalchemy>=2.0",
  "pydantic>=2.6",
  "pydantic-settings>=2.2",
  "python-jose[cryptography]>=3.3",
  "passlib[bcrypt]>=1.7",
  "python-multipart>=0.0.9",
  "jinja2>=3.1",
  "alembic>=1.13",
  "redis>=5.0",
  "celery>=5.3"
]

[tool.pytest.ini_options]
pythonpath = ["."]

```

## tests/test_calculator.py

```
from datetime import date
from decimal import Decimal

from app.calculations.debt_calculator import DebtCalculator, build_installment_options


def test_debt_calculator_returns_decimal_total():
    calc = DebtCalculator()
    result = calc.calculate(Decimal("1000.00"), date(2024, 1, 1), date(2024, 4, 1))
    assert result.total > Decimal("1000.00")


def test_installments_default_options():
    options = build_installment_options(Decimal("1200.00"))
    assert options[3] == Decimal("400.00")
    assert options[12] == Decimal("100.00")

```

