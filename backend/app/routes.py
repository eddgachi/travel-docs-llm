# backend/app/routes.py
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .models import ApplicationConfig, TravelDocumentQuery
from .schemas import (
    ApplicationConfigCreate,
    ApplicationConfigSchema,
    ApplicationConfigUpdate,
    TravelDocumentQuerySchema,
    TravelDocumentRequest,
    TravelDocumentResponse,
)
from .services import (
    DEFAULT_CONFIGS,
    get_config_value,
    query_travel_documents,
    seed_default_configs,
)
from .session import get_db

router = APIRouter(prefix="/api", tags=["Travel Documents"])


@router.get("/")
def read_root():
    return {"message": "Travel Documents Advisor API"}


@router.post(
    "/ask",
    response_model=TravelDocumentResponse,
    summary="Get travel document requirements",
)
def ask_travel_documents(
    request: TravelDocumentRequest,
    db: Session = Depends(get_db),
):
    """
    Get travel document requirements between two countries.
    Returns structured information about visa documents, passport requirements,
    additional documents, and travel advisories.
    """
    return query_travel_documents(db, request.origin, request.destination)


@router.get(
    "/history",
    response_model=List[TravelDocumentQuerySchema],
    summary="Get query history",
)
def get_query_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Retrieve the history of travel document queries with pagination.
    """
    enable_history = get_config_value(db, "enable_history", "true").lower() == "true"
    if not enable_history:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Query history is disabled in application settings.",
        )

    queries = db.query(TravelDocumentQuery).offset(skip).limit(limit).all()

    # Convert JSON strings back to lists
    result = []
    for query in queries:
        result.append(
            {
                "id": query.id,
                "origin_country": query.origin_country,
                "destination_country": query.destination_country,
                "visa_documents": json.loads(query.visa_documents),
                "passport_requirements": json.loads(query.passport_requirements),
                "additional_documents": json.loads(query.additional_documents),
                "travel_advisories": json.loads(query.travel_advisories),
                "queried_at": query.queried_at,
            }
        )

    return result


# Application Config Endpoints (similar to SME example)
@router.get("/settings", response_model=List[ApplicationConfigSchema])
def get_all_settings(db: Session = Depends(get_db)):
    settings = db.query(ApplicationConfig).all()
    for setting in settings:
        if setting.config_key == "google_api_key" and setting.config_value:
            setting.config_value = "********"
    return settings


@router.post(
    "/settings",
    response_model=ApplicationConfigSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_setting(
    setting_create: ApplicationConfigCreate, db: Session = Depends(get_db)
):
    db_setting = ApplicationConfig(
        id=setting_create.config_key,
        config_key=setting_create.config_key,
        config_value=setting_create.config_value,
        description=setting_create.description,
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


@router.put("/settings/{config_key}", response_model=ApplicationConfigSchema)
def update_setting(
    config_key: str,
    setting_update: ApplicationConfigUpdate,
    db: Session = Depends(get_db),
):
    db_setting = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )

    update_data = setting_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if (
            key == "config_value"
            and config_key == "google_api_key"
            and value == "********"
        ):
            continue
        setattr(db_setting, key, value)

    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)

    if db_setting.config_key == "google_api_key" and db_setting.config_value:
        db_setting.config_value = "********"

    return db_setting
