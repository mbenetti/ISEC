#!/usr/bin/env python3
"""
ISEC Project Setup Verification Script

This script verifies that the ISEC project is properly set up with all
dependencies installed and the environment configured correctly.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check Python version meets requirements."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")

    # Check against pyproject.toml requirements (>=3.12)
    if version.major == 3 and version.minor >= 12:
        print("   ✅ Python version meets requirements (>=3.12)")
        return True
    else:
        print(
            f"   ❌ Python version 3.12+ required, found {version.major}.{version.minor}"
        )
        return False


def check_uv_installed():
    """Check if uv is available."""
    print("\n🔍 Checking if uv is installed...")
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ uv is installed: {version}")
            return True
        else:
            print("   ❌ uv is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("   ❌ uv is not installed or not in PATH")
        return False


def check_virtual_environment():
    """Check if running in a virtual environment."""
    print("\n🔍 Checking virtual environment...")
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print(f"   ✅ Running in virtual environment")
        print(f"   Python executable: {sys.executable}")
        return True
    else:
        print("   ⚠️  Not running in a virtual environment")
        print("   Consider activating: source .venv/bin/activate")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")

    dependencies = [
        ("numpy", "1.24.0"),
        ("pandas", "2.0.0"),
        ("openpyxl", "3.0.0"),
        ("dotenv", "1.0.0"),  # python-dotenv
        ("chromadb", "1.4.0"),
        ("ollama", "0.6.0"),
        ("fastapi", "0.128.0"),
        ("uvicorn", "0.40.0"),
        ("jinja2", "3.1.6"),
        ("python_multipart", "0.0.22"), # python-multipart -> python_multipart
        ("matplotlib", "3.7.0"),
        ("pydantic", "2.0.0"),
        ("scipy", "1.10.0"),
    ]

    all_installed = True

    for package, min_version in dependencies:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                print(f"   ❌ {package} is not installed")
                all_installed = False
                continue

            # Try to get version
            try:
                module = __import__(package)
                version = getattr(module, "__version__", "unknown")
                print(f"   ✅ {package} {version} (required: >= {min_version})")

                # Simple version check (basic)
                if version != "unknown":
                    try:
                        from packaging import version as packaging_version

                        if packaging_version.parse(version) >= packaging_version.parse(
                            min_version
                        ):
                            print(f"      ✅ Version meets requirement")
                        else:
                            print(f"      ⚠️  Version may be too old")
                    except ImportError:
                        # packaging not available, skip version check
                        pass

            except AttributeError:
                print(f"   ✅ {package} installed (version unknown)")

        except ImportError:
            print(f"   ❌ {package} is not installed")
            all_installed = False

    return all_installed


def check_project_files():
    """Check if all project files exist."""
    print("\n🔍 Checking project files...")

    required_files = [
        "pyproject.toml",
        "README.md",
        "SETUP.md",
        "matriz_costo_caracteres.py",
        "Distancia_Semantica.py",
        "ISEC.py",
        "config.py",
    ]

    optional_files = [
        "quickstart.py",
        "setup_demo.sh",
        ".gitignore",
        "app/main.py",
    ]

    all_required_exist = True

    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
            all_required_exist = False

    print("\n   Optional files:")
    for file in optional_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} (not found)")

    return all_required_exist


def check_module_import():
    """Check if the main module can be imported."""
    print("\n🔍 Checking module import...")

    try:
        # Try to import the main module
        from matriz_costo_caracteres import (
            EditCostCalculator,
            create_default_calculator,
        )

        print("   ✅ Successfully imported matriz_costo_caracteres module")

        # Try to create an instance
        try:
            calculator = create_default_calculator()
            print("   ✅ Successfully created default calculator")

            # Test basic functionality
            test_strings = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
            all_chars = set()
            for s in test_strings:
                all_chars.update(s)
            calculator.setup_characters(list(all_chars))
            print("   ✅ Successfully set up characters")

            # Test costs (just check if they return numbers)
            cost = calculator.get_substitution_cost(test_strings[0][0], test_strings[0][1])
            assert isinstance(cost, (int, float))
            print("   ✅ Cost calculator is functional")

            return True

        except Exception as e:
            print(f"   ❌ Error creating/using matrix: {e}")
            return False

    except ImportError as e:
        print(f"   ❌ Failed to import module: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def run_basic_test():
    """Run the basic test file if it exists."""
    print("\n🔍 Running basic tests...")

    test_file = "test_basic.py"
    if not Path(test_file).exists():
        print(f"   ⚠️  {test_file} not found, skipping tests")
        return None

    try:
        result = subprocess.run(
            [sys.executable, test_file], capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            print("   ✅ Basic tests passed")
            # Show last few lines of output
            lines = result.stdout.strip().split("\n")
            if len(lines) > 3:
                print(f"      ... {lines[-3]}")
                print(f"      ... {lines[-2]}")
                print(f"      ... {lines[-1]}")
            else:
                for line in lines:
                    print(f"      {line}")
            return True
        else:
            print(f"   ❌ Basic tests failed (exit code: {result.returncode})")
            if result.stderr:
                print(f"      Error: {result.stderr[:200]}...")
            return False

    except Exception as e:
        print(f"   ❌ Error running tests: {e}")
        return False


def main():
    """Main verification function."""
    print("=" * 60)
    print("ISEC Project Setup Verification")
    print("=" * 60)
    print()

    checks = []

    # Run all checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("UV Installation", check_uv_installed()))
    checks.append(("Virtual Environment", check_virtual_environment()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Project Files", check_project_files()))
    checks.append(("Module Import", check_module_import()))

    test_result = run_basic_test()
    if test_result is not None:
        checks.append(("Basic Tests", test_result))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(checks)

    for name, result in checks:
        if result:
            passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 SETUP VERIFIED SUCCESSFULLY!")
        print("The ISEC project is ready to use.")
        print("\nNext steps:")
        print("1. Run the main example: python matriz_costo_caracteres.py")
        print("2. Check SETUP.md for more usage instructions")
        print("3. Review README.md for detailed documentation")
        return 0
    else:
        print(f"\n⚠️  SETUP INCOMPLETE ({total - passed} issues found)")
        print("\nRecommended actions:")
        print(
            "1. Ensure uv is installed: curl -LsSf https://astral.sh/uv/install.sh | sh"
        )
        print("2. Ensure Python 3.12+ is installed")
        print("3. Create virtual environment: uv venv")
        print("4. Activate it: source .venv/bin/activate")
        print("5. Install dependencies: uv sync")
        print("6. Run this verification again: python verify_setup.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
