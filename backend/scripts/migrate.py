#!/usr/bin/env python3
"""
Script para ejecutar migraciones de Alembic
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from app.core.config import settings


def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg = Config(str(backend_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return alembic_cfg


def upgrade_database(revision="head"):
    """Upgrade database to specified revision"""
    print(f"🔄 Upgrading database to revision: {revision}")
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, revision)
    print("✅ Database upgrade completed successfully")


def downgrade_database(revision):
    """Downgrade database to specified revision"""
    print(f"⬇️ Downgrading database to revision: {revision}")
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)
    print("✅ Database downgrade completed successfully")


def create_migration(message, autogenerate=True):
    """Create a new migration"""
    print(f"📝 Creating new migration: {message}")
    alembic_cfg = get_alembic_config()
    command.revision(alembic_cfg, message=message, autogenerate=autogenerate)
    print("✅ Migration created successfully")


def show_current_revision():
    """Show current database revision"""
    alembic_cfg = get_alembic_config()
    command.current(alembic_cfg)


def show_migration_history():
    """Show migration history"""
    alembic_cfg = get_alembic_config()
    command.history(alembic_cfg)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate.py upgrade [revision]     - Upgrade to revision (default: head)")
        print("  python migrate.py downgrade <revision>   - Downgrade to revision")
        print("  python migrate.py create <message>       - Create new migration")
        print("  python migrate.py current                - Show current revision")
        print("  python migrate.py history                - Show migration history")
        sys.exit(1)

    command_name = sys.argv[1]

    try:
        if command_name == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            upgrade_database(revision)

        elif command_name == "downgrade":
            if len(sys.argv) < 3:
                print("Error: downgrade requires a revision argument")
                sys.exit(1)
            revision = sys.argv[2]
            downgrade_database(revision)

        elif command_name == "create":
            if len(sys.argv) < 3:
                print("Error: create requires a message argument")
                sys.exit(1)
            message = " ".join(sys.argv[2:])
            create_migration(message)

        elif command_name == "current":
            show_current_revision()

        elif command_name == "history":
            show_migration_history()

        else:
            print(f"Unknown command: {command_name}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()