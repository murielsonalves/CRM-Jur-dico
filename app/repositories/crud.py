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
