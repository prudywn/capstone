FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MONGODB_URI=mongodb://mongo:27017
ENV KAFKA_BROKER=kafka:9092
ENV KAFKA_TOPIC=air_quality_events

CMD ["python", "main.py"]
