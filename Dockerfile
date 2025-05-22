FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["sh", "-c", "python cirisnode/db/init_db.py && uvicorn cirisnode.main:app --host 0.0.0.0 --port 8000 --workers 4"]
