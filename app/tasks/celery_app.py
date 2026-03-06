from celery import Celery

from app.core.config import settings

celery = Celery("crm_juridico", broker=settings.redis_url, backend=settings.redis_url)


@celery.task
def enviar_cobranca_async(titulo_id: int, canal: str):
    return {"titulo_id": titulo_id, "canal": canal, "status": "agendado"}
