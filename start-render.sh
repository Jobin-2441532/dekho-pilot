#!/bin/bash
# Render start script — dependencies already installed by buildCommand in render.yaml.
# DO NOT pip install here; the build step handles it.

echo "==> Starting ML Service in background on 127.0.0.1:8001..."
(
  cd ml_service
  export PYTHONPATH=$(pwd)
  python -m uvicorn main:app --host 127.0.0.1 --port 8001 2>&1 | sed 's/^/[ML] /'
) &
ML_PID=$!

# Give the ML service 3 seconds to bind before the main backend starts
sleep 3

echo "==> Starting Main Backend on port ${PORT:-10000}..."
cd backend
export PYTHONPATH=$(pwd)
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"
