#!/bin/bash
set -e

echo "=== Starting Unified Check-In System ==="

echo "[1/2] Starting FastAPI backend on port 8000..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "[2/2] Starting Vue frontend on port 5173..."
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
