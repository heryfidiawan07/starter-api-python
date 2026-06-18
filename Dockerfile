FROM python:3.12-slim
WORKDIR /app

# Install dependensi sistem untuk psycopg2 dan pyodbc
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p storage/photos

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
