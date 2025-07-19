#!/bin/bash

# Test script to simulate Railway deployment locally
echo "=== Testing Railway Deployment Locally ==="

# Activate virtual environment
source .venv/bin/activate

# Set Railway-like environment variables
export PORT=8000
export PYTHONPATH="."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Simulate Railway's working directory and file structure
echo "Current directory: $(pwd)"
echo "Files in root:"
ls -la | head -10

echo ""
echo "=== Testing module imports ==="
python -c "
try:
    import main
    print('✅ main.py imports successfully')
    print('✅ FastAPI app object:', type(main.app))
except Exception as e:
    print('❌ Import failed:', e)
    exit(1)
"

echo ""
echo "=== Testing gunicorn config check ==="
# Test the exact Railway command with config check
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5 --check-config

if [ $? -eq 0 ]; then
    echo "✅ Gunicorn config check passed"
else
    echo "❌ Gunicorn config check failed"
    exit 1
fi

echo ""
echo "=== Starting server for health check test ==="
# Start server in background for health check test
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5 --daemon --pid /tmp/test_server.pid

# Wait for server to start
sleep 5

echo "=== Testing health check endpoint ==="
# Test the health check endpoint
curl -f http://localhost:$PORT/healthz/ -o /tmp/health_response.json
health_status=$?

if [ $health_status -eq 0 ]; then
    echo "✅ Health check passed!"
    echo "Response:"
    cat /tmp/health_response.json
    echo ""
else
    echo "❌ Health check failed with status: $health_status"
fi

# Cleanup
if [ -f /tmp/test_server.pid ]; then
    kill $(cat /tmp/test_server.pid) 2>/dev/null
    rm /tmp/test_server.pid
fi

echo ""
echo "=== Test completed ==="
exit $health_status
