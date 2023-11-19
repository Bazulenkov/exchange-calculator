FROM python:3.10-alpine

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "tg_bot/bot.py"]
