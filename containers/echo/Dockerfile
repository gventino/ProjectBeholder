FROM python:3.9-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential python3-dev

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
