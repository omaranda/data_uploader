# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python
"""Initialize database schema."""

import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_uploader.config import Config


def main():
    """Initialize database schema."""
    load_dotenv()

    cfg = Config.from_env()

    print("Initializing database...")
    print(f"Host: {cfg.db_host}")
    print(f"Port: {cfg.db_port}")
    print(f"Database: {cfg.db_name}")
    print(f"User: {cfg.db_user}")

    try:
        # Connect to database
        conn = psycopg2.connect(
            host=cfg.db_host,
            port=cfg.db_port,
            database=cfg.db_name,
            user=cfg.db_user,
            password=cfg.db_password
        )

        # Read SQL file
        sql_file = Path(__file__).parent.parent / 'sql' / 'init.sql'

        with open(sql_file, 'r') as f:
            sql = f.read()

        # Execute SQL
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

        print("✅ Database initialized successfully!")

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
