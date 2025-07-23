# Database Migrations with Alembic

This document explains how to use Alembic for database migrations in the Colombian Electronic Invoicing System.

## Overview

Alembic is a database migration tool for SQLAlchemy. It allows you to:
- Create and manage database schema changes
- Version control your database structure
- Apply incremental updates to production databases
- Rollback changes when needed

## Configuration

### Files Structure
```
backend/
├── alembic.ini                    # Alembic configuration
├── migrations/
│   ├── env.py                     # Environment configuration
│   ├── script.py.mako            # Migration template
│   └── versions/                  # Migration files
│       └── 0001_initial_migration.py
├── scripts/
│   ├── migrate.py                 # Migration helper script
│   └── seed_data.py              # Initial data seeding
```

### Environment Variables

Make sure these environment variables are set:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/facturacion
```

## Common Operations

### 1. Apply Migrations

Apply all pending migrations:
```bash
cd backend
python scripts/migrate.py upgrade
```

Apply to specific revision:
```bash
python scripts/migrate.py upgrade 0001
```

### 2. Create New Migration

Create a new migration with auto-generated changes:
```bash
python scripts/migrate.py create "Add new column to products"
```

Create empty migration (manual):
```bash
python scripts/migrate.py create "Custom migration" --sql
```

### 3. Check Current Status

View current revision:
```bash
python scripts/migrate.py current
```

View migration history:
```bash
python scripts/migrate.py history
```

### 4. Rollback Changes

Rollback to previous revision:
```bash
python scripts/migrate.py downgrade -1
```

Rollback to specific revision:
```bash
python scripts/migrate.py downgrade 0001
```

### 5. Seed Initial Data

Populate database with initial data:
```bash
cd backend
python scripts/seed_data.py
```

## Docker Environment

### Using Docker Compose

Start database and apply migrations:
```bash
# Start PostgreSQL
docker-compose up -d db

# Apply migrations
docker-compose exec backend python scripts/migrate.py upgrade

# Seed initial data
docker-compose exec backend python scripts/seed_data.py
```

## Migration Best Practices

### 1. Review Generated Migrations
Always review auto-generated migrations before applying:
- Check column types and constraints
- Verify foreign key relationships
- Ensure data integrity

### 2. Test Migrations
Test migrations in development environment:
```bash
# Apply migration
python scripts/migrate.py upgrade

# Test application functionality

# Rollback if needed
python scripts/migrate.py downgrade -1
```

### 3. Backup Before Production
Always backup production database before applying migrations:
```bash
pg_dump -h localhost -U admin facturacion > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 4. Non-Destructive Changes
Prefer additive changes over destructive ones:
- Add new columns with default values
- Create new tables instead of modifying existing ones
- Use separate migrations for data transformations

## Colombian Invoicing Specific Notes

### Database Features
- **Multi-tenant**: All tables include `empresa_id` for company isolation
- **Audit trails**: Automatic `created_at` and `updated_at` timestamps
- **Colombian compliance**: Fields for NIT, document types, DIAN states
- **Tax calculations**: Support for IVA, INC, ICA Colombian taxes

### Triggers and Functions
The initial migration includes:
- `update_updated_at_column()` function for automatic timestamps
- Triggers on all main tables for `updated_at` field

### Initial Data
The seed script creates:
- Admin and User roles with appropriate permissions
- Test company with DIAN configuration
- Sample users, clients, and products
- Colombian tax and document type configurations

## Troubleshooting

### Common Issues

1. **Connection Error**
   ```
   Error: could not connect to database
   ```
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL is running
   - Verify database exists

2. **Import Error**
   ```
   ModuleNotFoundError: No module named 'app'
   ```
   - Ensure you're in the backend directory
   - Check Python path configuration in env.py

3. **Migration Conflict**
   ```
   Multiple heads detected
   ```
   - Merge migration branches using `alembic merge`
   - Create new migration to resolve conflicts

### Database Reset

To completely reset the database:
```bash
# Drop all tables
docker-compose exec db psql -U admin -d facturacion -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Apply all migrations
python scripts/migrate.py upgrade

# Seed initial data
python scripts/seed_data.py
```

## Production Deployment

### Automated Deployment
Include migrations in your deployment pipeline:
```bash
# 1. Backup database
pg_dump $DATABASE_URL > backup.sql

# 2. Apply migrations
python scripts/migrate.py upgrade

# 3. Verify application health
curl -f http://localhost:8000/health
```

### Rollback Plan
Always have a rollback plan:
1. Keep database backup before migration
2. Document rollback steps
3. Test rollback procedure in staging
4. Monitor application after deployment

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `migrate.py upgrade` | Apply all pending migrations |
| `migrate.py downgrade -1` | Rollback last migration |
| `migrate.py current` | Show current revision |
| `migrate.py history` | Show migration history |
| `migrate.py create "message"` | Create new migration |
| `seed_data.py` | Populate initial data |

For more information, see the [Alembic documentation](https://alembic.sqlalchemy.org/).