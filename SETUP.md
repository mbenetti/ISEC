# ISEC Project - Quick Setup Guide (Python 3.12+)

## Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows:
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Note: This project requires Python 3.12 or higher
   ```

2. **Verify installation**:
   ```bash
   uv --version
   ```

## Quick Setup (One-Liner)

```bash
# Create virtual environment and install dependencies
uv venv && source .venv/bin/activate && uv sync
```

## Step-by-Step Setup

### 1. Create Virtual Environment
```bash
uv venv
```

### 2. Activate Virtual Environment
- **macOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Verify Installation
```bash
# Run the verification script
python verify_setup.py
```

## Running the Project

### Run the App interface
```bash
python app/main.py
```

### Run the Command Line Example
```bash
python quickstart.py
```

## Development Setup

### Install Development Dependencies
```bash
uv sync --dev
```

### Development Commands
```bash
# Run tests
uv run pytest

# Format code
uv run black .

# Sort imports
uv run isort .
```

## Project Structure
```
ISEC/
├── app/                    # Web interface and API
├── datasets/               # Example datasets
├── pyproject.toml          # Project configuration
├── README.md               # Detailed documentation
├── SETUP.md                # This quick guide
├── ISEC.py                 # Main ISEC calculator
├── matriz_costo_caracteres.py  # Morphological distance implementation
├── Distancia_Semantica.py  # Semantic distance implementation
├── verify_setup.py         # Setup verification script
├── quickstart.py           # Quick start example
└── .gitignore              # Git ignore rules
```

## Common Commands

### Activate/Deactivate Environment
```bash
# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

### Update Dependencies
```bash
uv sync
```

### Clean Start
```bash
# Remove virtual environment and reinstall
rm -rf .venv
uv venv
source .venv/bin/activate
uv sync
```

## Troubleshooting

### uv Command Not Found
- Ensure uv is installed and in your PATH
- Restart your terminal after installation

### Python Version Issues
- This project requires Python 3.12 or higher
- uv automatically uses the appropriate Python version
- Check `pyproject.toml` for Python version requirements

### Dependency Installation Fails
- Check your internet connection
- Try clearing uv cache: `uv cache clean`
- Check for system dependencies (compilers, etc.)

## Need Help?
- Check the detailed [README.md](README.md)
- Run the setup demo: `./setup_demo.sh`
- Review the `pyproject.toml` for configuration details

---

**Next Steps:**
1. Set up the environment using the commands above
2. Run `python matriz_costo_caracteres.py` to see the example
3. Explore the code in `matriz_costo_caracteres.py`
4. Check `test_basic.py` for usage examples