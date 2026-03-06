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
