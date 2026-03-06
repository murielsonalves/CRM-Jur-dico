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
