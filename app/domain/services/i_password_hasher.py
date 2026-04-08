from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_text: str) -> str: ...

    @abstractmethod
    def verify(self, plain_text: str, hashed: str) -> bool: ...
