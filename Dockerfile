FROM python:3.9-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
COPY . .
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "5", "--port", "80"]
