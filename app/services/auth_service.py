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
