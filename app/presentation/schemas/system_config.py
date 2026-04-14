from typing import Optional

from pydantic import BaseModel, Field


class SystemConfigSet(BaseModel):
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(None, max_length=255)


class SystemConfigResponse(BaseModel):
    key: str
    value: str
    description: Optional[str]
