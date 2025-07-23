# Code Quality and Linting Configuration

This document explains the comprehensive code quality and linting setup for the Colombian Electronic Invoicing System.

## Overview

The project uses multiple tools to ensure code quality, consistency, and security:

- **Black**: Code formatting
- **isort**: Import organization
- **flake8**: Code linting and style checking
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanning
- **pre-commit**: Automated hooks for quality checks

## Tools Configuration

### Black (Code Formatting)

Black ensures consistent code formatting across the project.

**Configuration**: `pyproject.toml`
- Line length: 88 characters
- Target Python versions: 3.9, 3.10, 3.11
- Excludes migration files

```bash
# Format all code
black app tests scripts

# Check formatting without changing files
black --check app tests scripts
```

### isort (Import Sorting)

Automatically sorts and organizes imports according to PEP 8 standards.

**Configuration**: `pyproject.toml`
- Profile: black (compatible with Black)
- Known first-party modules: `app`
- Line length: 88 characters

```bash
# Sort imports
isort app tests scripts

# Check import sorting
isort --check-only app tests scripts
```

### flake8 (Linting)

Comprehensive linting tool that checks for:
- PEP 8 style violations
- Syntax errors
- Unused imports
- Code complexity
- Security issues

**Configuration**: `setup.cfg`
- Max line length: 88 (Black compatible)
- Max complexity: 10
- Excludes: migrations, build directories
- Special handling for Colombian naming conventions

```bash
# Run linting
flake8 app tests scripts

# Check specific files
flake8 app/models/factura.py
```

### mypy (Type Checking)

Static type checker that helps catch type-related errors.

**Configuration**: `mypy.ini` and `pyproject.toml`
- Strict type checking enabled
- Ignores missing type stubs for third-party libraries
- Less strict for test files

```bash
# Type check all code
mypy app tests scripts

# Check specific module
mypy app.models
```

### bandit (Security Scanning)

Scans code for common security vulnerabilities.

**Configuration**: `pyproject.toml`
- Excludes test directories
- Skips assert_used warnings (common in tests)

```bash
# Security scan
bandit -r app scripts

# Detailed report
bandit -r app -f json -o security-report.json
```

## Quick Commands

### Individual Tools

```bash
# Format code
black app tests scripts
isort app tests scripts

# Lint code
flake8 app tests scripts

# Type check
mypy app tests scripts

# Security check
bandit -r app scripts
```

### Automated Script

Use the comprehensive linting script for all checks:

```bash
# Run all checks
python scripts/lint.py --all

# Format code only
python scripts/lint.py --format

# Lint only
python scripts/lint.py --lint

# Type check only
python scripts/lint.py --type-check

# Security check only
python scripts/lint.py --security

# Check without fixing
python scripts/lint.py --check

# Clean up code (remove unused imports, upgrade syntax)
python scripts/lint.py --clean

# Run pre-commit hooks
python scripts/lint.py --pre-commit
```

## Pre-commit Hooks

Automated quality checks that run before each commit.

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Configuration

The `.pre-commit-config.yaml` file includes:

1. **Basic checks**: trailing whitespace, file endings, YAML/JSON validation
2. **Security**: Bandit security scanning
3. **Import sorting**: isort
4. **Code formatting**: Black
5. **Linting**: flake8 with plugins
6. **Type checking**: mypy
7. **SQL formatting**: SQLFluff for PostgreSQL
8. **Dockerfile linting**: hadolint
9. **Code upgrades**: pyupgrade for modern Python syntax
10. **Unused code removal**: autoflake

### Hooks Behavior

- **Auto-fix**: Some hooks automatically fix issues (Black, isort, autoflake)
- **Check-only**: Others report issues that need manual fixing (mypy, bandit)
- **Fail-fast**: Commit is blocked if any hook fails

## Development Workflow

### Daily Development

1. **Before committing**:
   ```bash
   python scripts/lint.py --all
   ```

2. **Quick formatting**:
   ```bash
   python scripts/lint.py --format
   ```

3. **Check before push**:
   ```bash
   python scripts/lint.py --check
   ```

### IDE Integration

#### VS Code

Add to `.vscode/settings.json`:

```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.sortImports.args": ["--profile", "black"]
}
```

#### PyCharm

1. Go to Settings → Tools → External Tools
2. Add Black, flake8, and mypy as external tools
3. Configure File Watchers for automatic formatting

### Continuous Integration

For GitHub Actions, add to your workflow:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements-dev.txt

- name: Run linting
  run: |
    python scripts/lint.py --all

- name: Run type checking
  run: |
    mypy app tests scripts

- name: Run security check
  run: |
    bandit -r app scripts
```

## Configuration Files

### File Structure

```
backend/
├── pyproject.toml           # Black, isort, mypy, coverage config
├── setup.cfg               # flake8 configuration
├── mypy.ini                # Detailed mypy settings
├── .pre-commit-config.yaml # Pre-commit hooks
├── requirements-dev.txt    # Development dependencies
└── scripts/lint.py         # Automated linting script
```

### Custom Rules for Colombian Context

The configuration includes special handling for:

1. **Spanish naming**: Relaxed naming rules for Spanish terms
2. **Document types**: CC, NIT, CE validation patterns
3. **DIAN compliance**: Special handling for Colombian tax terms
4. **Currency formatting**: Colombian peso formatting rules

## Troubleshooting

### Common Issues

1. **Black and flake8 conflicts**:
   - Solution: Use Black-compatible flake8 settings (already configured)

2. **Import sorting issues**:
   - Solution: Use `isort --profile black`

3. **mypy missing stubs**:
   - Solution: Install type stubs or add to ignore list in mypy.ini

4. **Pre-commit hooks failing**:
   ```bash
   # Update hooks
   pre-commit autoupdate
   
   # Clear cache
   pre-commit clean
   
   # Reinstall
   pre-commit uninstall
   pre-commit install
   ```

### Performance Optimization

1. **Skip slow checks during development**:
   ```bash
   SKIP=mypy,bandit git commit -m "Quick fix"
   ```

2. **Run checks in parallel**:
   ```bash
   python scripts/lint.py --format &
   python scripts/lint.py --lint &
   wait
   ```

### IDE Performance

1. **Disable real-time mypy** for large projects
2. **Use flake8 select mode** for faster linting
3. **Configure file watchers** to run only on save

## Customization

### Adding New Rules

1. **flake8 plugins**: Add to `requirements-dev.txt` and configure in `setup.cfg`
2. **mypy plugins**: Add to mypy configuration
3. **Pre-commit hooks**: Add new repos to `.pre-commit-config.yaml`

### Project-specific Ignores

Add to configuration files:

```ini
# setup.cfg - flake8
per-file-ignores =
    app/models/colombian_specific.py:N815,N816

# mypy.ini
[mypy-app.legacy.*]
ignore_errors = True
```

## Best Practices

### Code Quality Guidelines

1. **Always run linter before committing**
2. **Fix linting issues promptly**
3. **Use type hints for all functions**
4. **Write docstrings for public functions**
5. **Keep complexity under 10**
6. **Use meaningful variable names**

### Colombian Development Standards

1. **Document types**: Use proper validation for CC, NIT, CE
2. **Currency handling**: Always use Decimal for monetary values
3. **Tax calculations**: Include proper IVA, INC, ICA handling
4. **DIAN compliance**: Follow Colombian electronic invoicing standards

### Performance Considerations

1. **Line length**: 88 characters (Black standard)
2. **Import organization**: Group by type (standard, third-party, local)
3. **Type checking**: Use Union types for Colombian document types
4. **Security**: Never commit secrets or API keys

## Metrics and Reporting

### Code Quality Metrics

- **Complexity**: McCabe complexity < 10
- **Coverage**: Minimum 80% test coverage
- **Type coverage**: mypy strict mode
- **Security**: Zero bandit warnings

### Automated Reporting

```bash
# Generate coverage report
coverage run -m pytest
coverage report
coverage html

# Generate type checking report
mypy --html-report mypy-report app

# Generate security report
bandit -r app -f json -o security-report.json
```

---

For more information, see:
- [Black documentation](https://black.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)