# backend/app/services.py
import json
from typing import Any, Optional

import google.generativeai as genai
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import ApplicationConfig, TravelDocumentQuery

# Default configuration for Travel Documents Advisor
DEFAULT_CONFIGS = [
    {
        "config_key": "google_api_key",
        "config_value": "",
        "description": "Your Google AI API Key (required for Gemini models)",
    },
    {
        "config_key": "llm_model",
        "config_value": "gemini-1.5-flash-latest",
        "description": "Which LLM model to use for document generation",
    },
    {
        "config_key": "llm_temperature",
        "config_value": "0.3",
        "description": "Controls creativity of the responses (0.0 to 1.0)",
    },
    {
        "config_key": "enable_history",
        "config_value": "true",
        "description": "Whether to save query history",
    },
    {
        "config_key": "default_response_language",
        "config_value": "English",
        "description": "Default language for responses",
    },
]


def check_configs_exist(db: Session) -> bool:
    """Check if any config records exist in the database."""
    return db.query(ApplicationConfig.id).limit(1).first() is not None


def seed_default_configs(db: Session):
    """Seed the database with default configuration settings."""
    for cfg_data in DEFAULT_CONFIGS:
        config_key = cfg_data["config_key"]
        existing_config = (
            db.query(ApplicationConfig)
            .filter(ApplicationConfig.config_key == config_key)
            .first()
        )

        if existing_config:
            needs_update = False
            if existing_config.config_value != cfg_data["config_value"]:
                existing_config.config_value = cfg_data["config_value"]
                needs_update = True
            if existing_config.description != cfg_data["description"]:
                existing_config.description = cfg_data["description"]
                needs_update = True
            if needs_update:
                db.add(existing_config)
        else:
            new_config = ApplicationConfig(
                id=config_key,
                config_key=config_key,
                config_value=cfg_data["config_value"],
                description=cfg_data["description"],
            )
            db.add(new_config)
    db.commit()


def get_config_value(
    db: Session, config_key: str, default: Optional[Any] = None
) -> Optional[Any]:
    """Retrieve a configuration value from the database."""
    config_item = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )
    return config_item.config_value if config_item else default


def get_google_api_key(db: Session) -> str:
    """Retrieve the Google API key from the database."""
    api_key = get_config_value(db, "google_api_key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google API key is not configured. Please set it in the application settings.",
        )
    return api_key


def query_travel_documents(db: Session, origin: str, destination: str) -> dict:
    """Query the LLM for travel document requirements between two countries."""
    api_key = get_google_api_key(db)
    llm_model = get_config_value(db, "llm_model", "gemini-1.5-flash-latest")
    temperature = float(get_config_value(db, "llm_temperature", "0.3"))
    enable_history = get_config_value(db, "enable_history", "true").lower() == "true"
    response_language = get_config_value(db, "default_response_language", "English")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(llm_model)

    prompt = f"""
    Provide a detailed list of travel document requirements for traveling from {origin} to {destination}.
    Structure your response as a JSON object with exactly these four fields:
    - "visa_documents": array of strings listing required visa application documents
    - "passport_requirements": array of strings listing passport requirements
    - "additional_documents": array of strings listing other required documents
    - "advisories": array of strings listing important travel advisories
    
    All responses should be in {response_language} language.
    Be concise but thorough. Include any COVID-19 requirements if applicable.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
            ),
        )

        # Parse the response
        if response and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    try:
                        result = json.loads(part.text)
                        # Validate the structure
                        if not all(
                            key in result
                            for key in [
                                "visa_documents",
                                "passport_requirements",
                                "additional_documents",
                                "advisories",
                            ]
                        ):
                            raise ValueError("Invalid response structure from LLM")

                        # Save to history if enabled
                        if enable_history:
                            db_query = TravelDocumentQuery(
                                origin_country=origin,
                                destination_country=destination,
                                visa_documents=json.dumps(result["visa_documents"]),
                                passport_requirements=json.dumps(
                                    result["passport_requirements"]
                                ),
                                additional_documents=json.dumps(
                                    result["additional_documents"]
                                ),
                                travel_advisories=json.dumps(result["advisories"]),
                            )
                            db.add(db_query)
                            db.commit()

                        return result
                    except json.JSONDecodeError:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to parse LLM response as JSON",
                        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No valid response received from LLM",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying LLM: {str(e)}",
        )
