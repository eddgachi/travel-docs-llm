# backend/app/models.py
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .session import Base


class ApplicationConfig(Base):
    __tablename__ = "application_config"

    id = Column(String(50), primary_key=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ApplicationConfig(key='{self.config_key}', value='{self.config_value[:50]}...')>"


class TravelDocumentQuery(Base):
    __tablename__ = "travel_document_queries"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin_country = Column(String(100), nullable=False)
    destination_country = Column(String(100), nullable=False)
    visa_documents = Column(Text)  # JSON string
    passport_requirements = Column(Text)  # JSON string
    additional_documents = Column(Text)  # JSON string
    travel_advisories = Column(Text)  # JSON string
    queried_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TravelDocumentQuery(origin='{self.origin_country}', destination='{self.destination_country}')>"
