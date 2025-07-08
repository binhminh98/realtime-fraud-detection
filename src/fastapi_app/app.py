"""
Main app backend module for FastAPI app.
"""

from endpoints.inference_endpoints import router as inference_router
from endpoints.models_endpoints import router as model_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(model_router)
app.include_router(inference_router)


@app.get("/")
async def root():
    return {
        "message": "Test backend app for realtime fraud detection project!"
    }
