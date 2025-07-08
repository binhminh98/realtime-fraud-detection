"""
Module to specify inference endpoints for fraud detection ML models.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from services.inference_services import InferenceServices

from models.models import Transaction, TransactionPrediction

router = APIRouter()

router = APIRouter(
    prefix="/inference",
    tags=["inference"],
)


@router.post("/")
async def inference(item: Transaction) -> TransactionPrediction:
    try:
        response = InferenceServices.inference(item.model_dump())

        if response:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=response
            )

        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="Cannot do inference!",
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=str(e)
        )
