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
