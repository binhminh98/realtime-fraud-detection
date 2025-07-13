FROM python:3.10.9-slim

WORKDIR /fastapi_app

COPY . /fastapi_app/

# Install system dependencies needed to build psutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    build-essential \
    && pip install --no-cache-dir psutil==5.9.8 \
    && rm -rf /var/lib/apt/lists/*

# Requirements to run fastapi
RUN pip install --no-cache-dir -r /fastapi_app/requirements.txt

# Expose port
EXPOSE 80

# Run app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]