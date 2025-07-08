FROM python:3.10.9

WORKDIR /fastapi_app

COPY . /fastapi_app/

# Requirements to run fastapi
RUN pip install --no-cache-dir -r /fastapi_app/requirements.txt

# Expose port
EXPOSE 80

# Run app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]