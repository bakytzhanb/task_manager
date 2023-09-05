FROM python:3.11.3-slim-buster

WORKDIR /app/
COPY requirements.txt .

RUN buildDeps="build-essential libpq-dev" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    && pip install -U pip && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

EXPOSE 8000
CMD ["python", "/app/manage.py runserver 0.0.0.0:8000"]