# backend/app/routes.py
import json
from datetime import datetime
from typing import List
from uuid import UUID

import google.generativeai as genai  # Import the Google Generative AI library
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
from .services import get_config_value, get_google_api_key
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

    Example request:
    {
        "origin": "Kenya",
        "destination": "Ireland"
    }

    Example response:
    {
        "visa_documents": ["Valid visa application form", "Passport photos"],
        "passport_requirements": ["Valid for 6 months", "2 blank pages"],
        "additional_documents": ["Return ticket", "Proof of funds"],
        "advisories": ["Check COVID requirements", "Register with embassy"]
    }
    """
    try:
        # Get configuration values
        api_key = get_google_api_key(db)
        llm_model = get_config_value(db, "llm_model", "gemini-1.5-flash-latest")
        temperature = float(get_config_value(db, "llm_temperature", "0.3"))
        enable_history = (
            get_config_value(db, "enable_history", "true").lower() == "true"
        )
        response_language = get_config_value(db, "default_response_language", "English")

        # Configure Gemini client
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(llm_model)

        # Create the prompt with clear instructions for structured output
        prompt = f"""
        You are a travel document expert. Provide detailed requirements for traveling from {request.origin} to {request.destination}.
        
        Respond with a JSON object having exactly these fields:
        - "visa_documents": array of strings listing required visa documents
        - "passport_requirements": array of strings listing passport requirements
        - "additional_documents": array of strings listing other required documents
        - "advisories": array of strings listing important travel advisories
        
        Requirements:
        1. Be accurate and up-to-date (current year is {datetime.now().year})
        2. Include any COVID-19 requirements if applicable
        3. Response must be in {response_language}
        4. Each array should have at least 2 items
        5. Format for direct JSON parsing
        
        Example structure:
        {{
            "visa_documents": ["item1", "item2"],
            "passport_requirements": ["item1", "item2"],
            "additional_documents": ["item1", "item2"],
            "advisories": ["item1", "item2"]
        }}
        """

        # Make the API call to Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
            ),
        )

        # Parse and validate the response
        if not response or not response.candidates:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No response received from Gemini API",
            )

        # Extract text from the first candidate
        response_text = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text"):
                response_text = part.text
                break

        if not response_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Empty response from Gemini API",
            )

        # Clean the response (sometimes Gemini adds markdown formatting)
        cleaned_response = (
            response_text.strip().replace("```json", "").replace("```", "").strip()
        )

        try:
            result = json.loads(cleaned_response)

            # Validate the response structure
            required_fields = [
                "visa_documents",
                "passport_requirements",
                "additional_documents",
                "advisories",
            ]
            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in response")

            # Convert all values to lists if they aren't already
            for field in required_fields:
                if not isinstance(result[field], list):
                    result[field] = [str(result[field])]

            # Save to history if enabled
            if enable_history:
                db_query = TravelDocumentQuery(
                    origin_country=request.origin,
                    destination_country=request.destination,
                    visa_documents=json.dumps(result["visa_documents"]),
                    passport_requirements=json.dumps(result["passport_requirements"]),
                    additional_documents=json.dumps(result["additional_documents"]),
                    travel_advisories=json.dumps(result["advisories"]),
                )
                db.add(db_query)
                db.commit()

            return result

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse Gemini response: {str(e)}. Response was: {response_text}",
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid response structure from Gemini: {str(e)}",
            )

    except HTTPException:
        raise  # Re-raise existing HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing travel document request: {str(e)}",
        )


@router.get("/recent-queries", response_model=List[TravelDocumentQuerySchema])
def get_recent_queries(limit: int = 5, db: Session = Depends(get_db)):
    """
    Get recent travel document queries (for dashboard sidebar)
    """
    queries = (
        db.query(TravelDocumentQuery)
        .order_by(TravelDocumentQuery.queried_at.desc())
        .limit(limit)
        .all()
    )

    # Convert JSON strings back to lists
    result = []
    for query in queries:
        result.append(
            {
                "id": query.id,
                "origin_country": query.origin_country,
                "destination_country": query.destination_country,
                "queried_at": query.queried_at,
                "visa_documents": json.loads(query.visa_documents),
                "passport_requirements": json.loads(query.passport_requirements),
                "additional_documents": json.loads(query.additional_documents),
                "travel_advisories": json.loads(query.travel_advisories),
            }
        )
    return result


@router.get("/query/{query_id}", response_model=TravelDocumentQuerySchema)
def get_query_details(query_id: UUID, db: Session = Depends(get_db)):
    """
    Get details of a specific query
    """
    query = (
        db.query(TravelDocumentQuery).filter(TravelDocumentQuery.id == query_id).first()
    )

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Query not found"
        )

    return {
        "id": query.id,
        "origin_country": query.origin_country,
        "destination_country": query.destination_country,
        "visa_documents": json.loads(query.visa_documents),
        "passport_requirements": json.loads(query.passport_requirements),
        "additional_documents": json.loads(query.additional_documents),
        "travel_advisories": json.loads(query.travel_advisories),
        "queried_at": query.queried_at,
    }


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
