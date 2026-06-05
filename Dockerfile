FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema para pdfplumber / pymupdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copia o projeto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
