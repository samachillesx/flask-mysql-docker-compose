FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

# Use this for local development
# CMD ["python", "app.py"]

# Gunicorn, a Python web server used to run Python web applications
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]