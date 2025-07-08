"""
Module to specify models endpoints for fraud detection ML models.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from services.models_services import ModelServices

from models.models import ModelInfo

router = APIRouter()

router = APIRouter(
    prefix="/models",
    tags=["models"],
)


@router.get("/")
async def get_model_names() -> list | None:
    try:
        response = ModelServices.get_model_names()

        if response:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=response
            )

        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="No models have been registered!",
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=str(e)
        )


@router.get("/champion")
async def get_champion_model() -> ModelInfo:
    try:
        response = ModelServices.get_champion_model_info()

        if response:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=response
            )

        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="No champion model found!",
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=str(e)
        )


@router.get("/{model_name}")
async def get_model_info_by_name(model_name: str) -> ModelInfo:
    try:
        response = ModelServices.get_model_info_by_name(model_name)

        if response:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=response
            )

        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=f"Model {model_name} doesn't exist!",
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=str(e)
        )
