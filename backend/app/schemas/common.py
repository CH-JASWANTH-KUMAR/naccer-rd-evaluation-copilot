from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
