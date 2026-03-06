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
