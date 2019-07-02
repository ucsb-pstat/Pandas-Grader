set -x
pgrep uvicorn | xargs kill -9 || true
uvicorn app:app --host "0.0.0.0" --port 8000
