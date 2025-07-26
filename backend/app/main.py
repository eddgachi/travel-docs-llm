# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routes import router
from .services import check_configs_exist, seed_default_configs
from .session import SessionLocal

origins = [
    "http://localhost:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        if not check_configs_exist(db):
            seed_default_configs(db)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    description = """
    Travel Documents Advisor API

    This service provides structured information about travel document requirements
    between any two countries, including visa documents, passport requirements,
    additional documents, and travel advisories.

    Powered by Google Gemini AI.
    """

    openapi_schema = get_openapi(
        title="Travel Documents Advisor API",
        version="1.0.0",
        description=description,
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
