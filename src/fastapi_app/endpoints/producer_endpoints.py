"""
Module to specify transaction producers endpoints.
"""

from fastapi import APIRouter, BackgroundTasks, status
from fastapi.responses import JSONResponse
from services.producer_services import ProducerService

router = APIRouter()

router = APIRouter(
    prefix="/producers",
    tags=["producers"],
)


@router.get("/")
async def get_producers() -> JSONResponse:
    try:
        response = ProducerService.get_producers()

        if response:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=response
            )

        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="No producers found!",
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=str(e)
        )


@router.post("/produce_transactions/{num_messages}")
async def produce_transactions(
    num_messages: int, background_tasks: BackgroundTasks
) -> JSONResponse:
    try:
        background_tasks.add_task(
            ProducerService.produce_transactions, num_messages
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f"Kafka has started producing {num_messages} transactions!",
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=str(e)
        )
