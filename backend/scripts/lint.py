#!/usr/bin/env python3
"""
Linting and code quality script for Colombian Electronic Invoicing System

This script provides automated code quality checks including:
- Code formatting with Black
- Import sorting with isort
- Linting with flake8
- Type checking with mypy
- Security scanning with bandit
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'


def print_banner(text: str, color: str = Colors.BLUE) -> None:
    """Print a colored banner"""
    print(f"\n{color}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.RESET}\n")


def run_command(command: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command and handle output"""
    cmd_str = ' '.join(command)
    print(f"{Colors.CYAN}🔄 Running: {cmd_str}{Colors.RESET}")
    
    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=capture_output,
            text=True
        )
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {cmd_str} - Success{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ {cmd_str} - Failed{Colors.RESET}")
            if capture_output and result.stdout:
                print(result.stdout)
            if capture_output and result.stderr:
                print(result.stderr)
        
        return result
    
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ {cmd_str} - Failed with exit code {e.returncode}{Colors.RESET}")
        if capture_output and e.stdout:
            print(e.stdout)
        if capture_output and e.stderr:
            print(e.stderr)
        raise
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Command not found: {command[0]}{Colors.RESET}")
        print(f"   Make sure you have installed the development requirements:")
        print(f"   pip install -r requirements-dev.txt")
        raise


def format_code(paths: List[str], fix: bool = True) -> bool:
    """Format code with Black and isort"""
    print_banner("Code Formatting", Colors.PURPLE)
    
    success = True
    
    try:
        # Sort imports with isort
        isort_cmd = ["isort"]
        if not fix:
            isort_cmd.append("--check-only")
        isort_cmd.extend(paths)
        
        run_command(isort_cmd)
        
        # Format code with Black
        black_cmd = ["black"]
        if not fix:
            black_cmd.append("--check")
        black_cmd.extend(paths)
        
        run_command(black_cmd)
        
    except subprocess.CalledProcessError:
        success = False
    
    return success


def lint_code(paths: List[str]) -> bool:
    """Lint code with flake8"""
    print_banner("Code Linting", Colors.YELLOW)
    
    try:
        flake8_cmd = ["flake8"] + paths
        run_command(flake8_cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def type_check(paths: List[str]) -> bool:
    """Type check with mypy"""
    print_banner("Type Checking", Colors.BLUE)
    
    try:
        mypy_cmd = ["mypy"] + paths
        run_command(mypy_cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def security_check(paths: List[str]) -> bool:
    """Security check with bandit"""
    print_banner("Security Scanning", Colors.RED)
    
    try:
        bandit_cmd = ["bandit", "-r"] + paths
        run_command(bandit_cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def remove_unused_imports(paths: List[str]) -> bool:
    """Remove unused imports with autoflake"""
    print_banner("Removing Unused Imports", Colors.CYAN)
    
    try:
        autoflake_cmd = [
            "autoflake",
            "--in-place",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--remove-duplicate-keys",
            "--ignore-init-module-imports",
            "--recursive"
        ] + paths
        
        run_command(autoflake_cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def upgrade_syntax(paths: List[str]) -> bool:
    """Upgrade Python syntax with pyupgrade"""
    print_banner("Upgrading Python Syntax", Colors.GREEN)
    
    try:
        # Find all Python files
        python_files = []
        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file() and path_obj.suffix == '.py':
                python_files.append(str(path_obj))
            elif path_obj.is_dir():
                python_files.extend(str(f) for f in path_obj.rglob('*.py'))
        
        if python_files:
            pyupgrade_cmd = ["pyupgrade", "--py39-plus"] + python_files
            run_command(pyupgrade_cmd)
        
        return True
    except subprocess.CalledProcessError:
        return False


def run_pre_commit() -> bool:
    """Run pre-commit hooks"""
    print_banner("Pre-commit Hooks", Colors.PURPLE)
    
    try:
        # Install pre-commit hooks if not already installed
        run_command(["pre-commit", "install"])
        
        # Run pre-commit on all files
        run_command(["pre-commit", "run", "--all-files"])
        
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Lint and format code for Colombian Electronic Invoicing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/lint.py --all                 # Run all checks
  python scripts/lint.py --format              # Format code only
  python scripts/lint.py --lint                # Lint code only
  python scripts/lint.py --type-check          # Type check only
  python scripts/lint.py --security            # Security check only
  python scripts/lint.py --fix app/ tests/     # Format specific paths
  python scripts/lint.py --check               # Check without fixing
        """
    )
    
    parser.add_argument(
        "paths",
        nargs="*",
        default=["app", "tests", "scripts"],
        help="Paths to lint (default: app tests scripts)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks (format, lint, type-check, security)"
    )
    
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code with Black and isort"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Lint code with flake8"
    )
    
    parser.add_argument(
        "--type-check",
        action="store_true",
        help="Type check with mypy"
    )
    
    parser.add_argument(
        "--security",
        action="store_true",
        help="Security check with bandit"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove unused imports and upgrade syntax"
    )
    
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Run pre-commit hooks"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check only, don't fix issues"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # If no specific checks requested, run all
    if not any([args.format, args.lint, args.type_check, args.security, args.clean, args.pre_commit]):
        args.all = True
    
    print_banner("🇨🇴 Colombian Electronic Invoicing System - Code Quality", Colors.GREEN)
    print(f"Checking paths: {', '.join(args.paths)}")
    
    results = []
    
    try:
        if args.clean or args.all:
            results.append(("Remove unused imports", remove_unused_imports(args.paths)))
            results.append(("Upgrade syntax", upgrade_syntax(args.paths)))
        
        if args.format or args.all:
            results.append(("Format code", format_code(args.paths, fix=not args.check)))
        
        if args.lint or args.all:
            results.append(("Lint code", lint_code(args.paths)))
        
        if args.type_check or args.all:
            results.append(("Type check", type_check(args.paths)))
        
        if args.security or args.all:
            results.append(("Security check", security_check(args.paths)))
        
        if args.pre_commit:
            results.append(("Pre-commit hooks", run_pre_commit()))
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
    
    # Print summary
    print_banner("Summary", Colors.CYAN)
    
    failed_checks = []
    for check_name, success in results:
        status = f"{Colors.GREEN}✅" if success else f"{Colors.RED}❌"
        print(f"{status} {check_name}{Colors.RESET}")
        if not success:
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"\n{Colors.RED}❌ {len(failed_checks)} check(s) failed:{Colors.RESET}")
        for check in failed_checks:
            print(f"   - {check}")
        print(f"\n{Colors.YELLOW}💡 Fix the issues above and run the linter again{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}🎉 All checks passed! Your code is ready for commit.{Colors.RESET}")


if __name__ == "__main__":
    main()