FROM python:3.12-slim

# variaveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# dependencias do postgres
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# copiar código da aplicação
COPY . .

RUN mkdir -p staticfiles

EXPOSE 8000

# script de inicialização será executado pelo docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]