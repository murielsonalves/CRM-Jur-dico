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
