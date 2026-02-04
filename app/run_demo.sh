#!/bin/bash
# Enable immediate exit on error
set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

echo "Starting ISEC Demo Environment..."
echo "Use Ctrl+C to stop."

# Check if precalc is needed (if cache missing)
if [ ! -f "app/embeddings_cache.pkl" ]; then
    echo "First run detected. Pre-calculating embeddings..."
    uv run app/precalc.py
fi

# Run the app
echo "Open http://localhost:8000 in your browser."
uv run app/main.py
