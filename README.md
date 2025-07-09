# complaints-api

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

docker compose up --build -d

curl -L --location-trusted -i -X POST http://localhost:8000/complaints \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 203.0.113.45" \
  -d '{"text":"Test complaint"}'