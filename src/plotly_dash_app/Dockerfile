FROM python:3.10.9-slim

WORKDIR /plotly_dash_app

COPY . /plotly_dash_app/

# Requirements to run plotly dash app
RUN pip install --no-cache-dir -r /plotly_dash_app/requirements.txt

# Expose port
EXPOSE 8050

# Run app
CMD ["python", "app.py"]