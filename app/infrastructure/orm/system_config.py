from typing import Optional

from sqlalchemy import VARCHAR, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm.base import Base


class SystemConfigORM(Base):
    __tablename__ = "system_config"

    key: Mapped[str] = mapped_column(VARCHAR(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
