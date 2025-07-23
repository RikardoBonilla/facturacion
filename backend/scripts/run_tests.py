#!/usr/bin/env python3
"""
Script para ejecutar tests con diferentes configuraciones
"""

import sys
import subprocess
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    print(f"   Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e.stderr.strip()}")
        return False


def run_all_tests():
    """Run all tests with coverage"""
    return run_command(
        ["python", "-m", "pytest", "-v", "--cov=app", "--cov-report=html", "--cov-report=term"],
        "Running all tests with coverage"
    )


def run_unit_tests():
    """Run only unit tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/unit/", "-v", "-m", "unit"],
        "Running unit tests"
    )


def run_integration_tests():
    """Run only integration tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/integration/", "-v", "-m", "integration"],
        "Running integration tests"
    )


def run_auth_tests():
    """Run authentication-related tests"""
    return run_command(
        ["python", "-m", "pytest", "-v", "-m", "auth"],
        "Running authentication tests"
    )


def run_crud_tests():
    """Run CRUD operation tests"""
    return run_command(
        ["python", "-m", "pytest", "-v", "-m", "crud"],
        "Running CRUD tests"
    )


def run_fast_tests():
    """Run fast tests (unit tests)"""
    return run_command(
        ["python", "-m", "pytest", "-v", "-m", "unit", "--durations=5"],
        "Running fast tests"
    )


def run_coverage_report():
    """Generate detailed coverage report"""
    commands = [
        (["python", "-m", "pytest", "--cov=app", "--cov-report="], "Generating coverage data"),
        (["coverage", "html"], "Generating HTML coverage report"),
        (["coverage", "xml"], "Generating XML coverage report"),
        (["coverage", "report"], "Displaying coverage summary")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    print("📊 Coverage reports generated:")
    print("   HTML: htmlcov/index.html")
    print("   XML:  coverage.xml")
    return True


def run_tests_with_markers(markers):
    """Run tests with specific markers"""
    marker_str = " or ".join(markers)
    return run_command(
        ["python", "-m", "pytest", "-v", "-m", marker_str],
        f"Running tests with markers: {marker_str}"
    )


def check_test_database():
    """Check if test database is accessible"""
    try:
        import asyncio
        from sqlalchemy.ext.asyncio import create_async_engine
        
        async def test_connection():
            TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:5432/facturacion_test"
            engine = create_async_engine(TEST_DATABASE_URL)
            try:
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
                return True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            finally:
                await engine.dispose()
        
        result = asyncio.run(test_connection())
        if result:
            print("✅ Test database connection successful")
        return result
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_tests.py all           - Run all tests with coverage")
        print("  python run_tests.py unit          - Run unit tests only")
        print("  python run_tests.py integration   - Run integration tests only")
        print("  python run_tests.py auth          - Run authentication tests")
        print("  python run_tests.py crud          - Run CRUD tests")
        print("  python run_tests.py fast          - Run fast tests (unit)")
        print("  python run_tests.py coverage      - Generate coverage reports")
        print("  python run_tests.py check-db      - Check test database connection")
        print("  python run_tests.py markers <m1,m2> - Run tests with specific markers")
        sys.exit(1)

    command = sys.argv[1]
    
    # Change to backend directory
    import os
    os.chdir(backend_dir)
    
    success = True
    
    if command == "all":
        success = run_all_tests()
    elif command == "unit":
        success = run_unit_tests()
    elif command == "integration":
        success = run_integration_tests()
    elif command == "auth":
        success = run_auth_tests()
    elif command == "crud":
        success = run_crud_tests()
    elif command == "fast":
        success = run_fast_tests()
    elif command == "coverage":
        success = run_coverage_report()
    elif command == "check-db":
        success = check_test_database()
    elif command == "markers":
        if len(sys.argv) < 3:
            print("Error: markers command requires marker list")
            sys.exit(1)
        markers = sys.argv[2].split(",")
        success = run_tests_with_markers(markers)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    if success:
        print("\n🎉 Test execution completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test execution failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()