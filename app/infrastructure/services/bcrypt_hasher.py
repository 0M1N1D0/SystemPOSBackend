from passlib.context import CryptContext

from app.domain.services.i_password_hasher import IPasswordHasher

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptHasher(IPasswordHasher):
    def hash(self, plain_text: str) -> str:
        return _ctx.hash(plain_text)

    def verify(self, plain_text: str, hashed: str) -> bool:
        return _ctx.verify(plain_text, hashed)
