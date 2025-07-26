# backend/app/schemas.py
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# Application Config Schemas (similar to SME example)
class ApplicationConfigBase(BaseSchema):
    config_key: str = Field(
        ..., description="The unique key for the configuration setting."
    )
    config_value: str = Field(
        ..., description="The value of the configuration setting."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the config setting."
    )


class ApplicationConfigCreate(ApplicationConfigBase):
    pass


class ApplicationConfigUpdate(BaseSchema):
    config_key: Optional[str] = Field(
        None, description="The unique key for the configuration setting."
    )
    config_value: Optional[str] = Field(
        None, description="The value of the configuration setting."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the config setting."
    )


class ApplicationConfigSchema(ApplicationConfigBase):
    id: str


# Travel Document Schemas
class TravelDocumentRequest(BaseSchema):
    origin: str = Field(..., description="The origin country")
    destination: str = Field(..., description="The destination country")


class TravelDocumentResponse(BaseSchema):
    visa_documents: List[str] = Field(
        ..., description="List of required visa documents"
    )
    passport_requirements: List[str] = Field(..., description="Passport requirements")
    additional_documents: List[str] = Field(
        ..., description="Additional required documents"
    )
    advisories: List[str] = Field(..., description="Travel advisories")


class TravelDocumentQuerySchema(BaseSchema):
    id: uuid.UUID
    origin_country: str
    destination_country: str
    visa_documents: List[str]
    passport_requirements: List[str]
    additional_documents: List[str]
    travel_advisories: List[str]
    queried_at: datetime
