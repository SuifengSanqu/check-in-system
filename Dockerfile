FROM python:3.11-slim

RUN pip install --no-cache-dir fastapi uvicorn

WORKDIR /app
COPY backend/ /app/

EXPOSE 7860

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
