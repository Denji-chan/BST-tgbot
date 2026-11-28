FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Tashkent

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Root bo'lmagan foydalanuvchi bilan ishlaymiz
RUN useradd --create-home --uid 1000 bot && mkdir -p /app/logs && chown -R bot:bot /app
USER bot

CMD ["sh", "-c", "alembic upgrade head && python app.py"]
