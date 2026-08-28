from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    type: str = Field(default="ACADEMIC")
    location: str = Field(..., min_length=2, max_length=255)


class InstitutionUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    type: str | None = None
    location: str | None = None


class InstitutionRead(ORMBase):
    id: str
    name: str
    code: str
    type: str
    location: str
    created_at: datetime
    updated_at: datetime
