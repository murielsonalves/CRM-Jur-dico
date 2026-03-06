from fastapi import FastAPI

from app.api.routes import router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM Jurídico de Cobrança")
app.include_router(router, prefix="/api")


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
