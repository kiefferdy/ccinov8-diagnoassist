#!/usr/bin/env python3
"""
Test runner script for DiagnoAssist Backend
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_tests(test_type: str = "all", verbose: bool = False, coverage: bool = False):
    """Run tests based on type and options"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    # Test type selection
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "repository":
        cmd.extend(["-m", "repository"])
    elif test_type == "service":
        cmd.extend(["-m", "service"])
    elif test_type == "fhir":
        cmd.extend(["-m", "fhir"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)
    
    # Add tests directory
    cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run DiagnoAssist Backend tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "repository", "service", "fhir", "api", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Tests directory not found. Run this script from the backend root directory.")
        sys.exit(1)
    
    success = run_tests(args.type, args.verbose, args.coverage)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()