FROM python:3.12-slim

WORKDIR /app

COPY ai-server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ai-server/app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]

