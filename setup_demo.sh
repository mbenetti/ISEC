#!/bin/bash

# ISEC Project Setup Demo Script
# This script demonstrates how to set up the ISEC project using uv

set -e  # Exit on error

echo "========================================="
echo "ISEC Project Setup Demo"
echo "========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed: $(uv --version)"
echo ""

# Step 1: Create virtual environment
echo "Step 1: Creating virtual environment..."
uv venv
echo "✅ Virtual environment created in .venv/"
echo ""

# Step 2: Activate virtual environment (for demonstration)
echo "Step 2: Activating virtual environment..."
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated (macOS/Linux)"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    .venv\Scripts\activate
    echo "✅ Virtual environment activated (Windows)"
else
    echo "⚠️  Unknown OS, please activate manually:"
    echo "   - macOS/Linux: source .venv/bin/activate"
    echo "   - Windows: .venv\Scripts\activate"
fi
echo ""

# Step 3: Install dependencies
echo "Step 3: Installing dependencies..."
uv sync
echo "✅ Dependencies installed"
echo ""

# Step 4: Verify Python and packages
echo "Step 4: Verifying installation..."
echo "Python version: $(python --version)"
echo ""

# Check if numpy and pandas are installed
echo "Checking installed packages:"
python -c "import numpy; print(f'✅ numpy {numpy.__version__}')"
python -c "import pandas; print(f'✅ pandas {pandas.__version__}')"
echo ""

# Step 5: Run the main example
echo "Step 5: Running the main example..."
echo "-----------------------------------------"
python matriz_costo_caracteres.py
echo "-----------------------------------------"
echo ""

# Step 6: Run basic tests
echo "Step 6: Running basic tests..."
echo "-----------------------------------------"
python quickstart.py
echo "-----------------------------------------"
echo ""

# Step 7: Development setup (optional)
echo "Step 7: Setting up development environment..."
echo "To install development dependencies, run:"
echo "   uv sync --dev"
echo ""
echo "Development commands available after installing dev dependencies:"
echo "   uv run pytest      # Run tests"
echo "   uv run black .     # Format code"
echo "   uv run isort .     # Sort imports"
echo "   uv run flake8      # Lint code"
echo "   uv run mypy .      # Type checking"
echo ""

# Step 8: Deactivate virtual environment
echo "Step 8: Deactivating virtual environment..."
deactivate
echo "✅ Virtual environment deactivated"
echo ""

echo "========================================="
echo "Setup completed successfully! 🎉"
echo "========================================="
echo ""
echo "To start working on the project:"
echo "1. Activate the virtual environment:"
echo "   - macOS/Linux: source .venv/bin/activate"
echo "   - Windows: .venv\Scripts\activate"
echo ""
echo "2. Run your code:"
echo "   python matriz_costo_caracteres.py"
echo ""
echo "3. When done, deactivate:"
echo "   deactivate"
echo ""

# Make the script executable
chmod +x "$0"

echo "This script is now executable. Run it again with:"
echo "  ./setup_demo.sh"
