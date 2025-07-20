FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart 

COPY . .
CMD ["uvicorn", "demo.api_server:app", "--host", "0.0.0.0", "--port", "8000"] 