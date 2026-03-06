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
