"""Backup script for local PostgreSQL database.

Exports all 27 tables and data into JSON and SQL backup files in storage/backups/.
"""

import datetime
import json
import os
from decimal import Decimal
from typing import Any

from sqlalchemy import create_engine, inspect, text


class CustomEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)


def backup_local_database():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://naccer:naccerpass@localhost:5432/naccer_db")
    engine = create_engine(db_url)
    inspector = inspect(engine)

    backup_dir = os.path.join(os.path.dirname(__file__), "..", "storage", "backups")
    os.makedirs(backup_dir, exist_ok=True)

    json_backup_file = os.path.join(backup_dir, "local_db_backup.json")
    tables = inspector.get_table_names()

    full_data: dict[str, list[dict[str, Any]]] = {}
    total_rows_backed_up = 0

    with engine.connect() as conn:
        for table in tables:
            rows_result = conn.execute(text(f'SELECT * FROM "{table}"')).mappings().all()
            table_rows = [dict(row) for row in rows_result]
            full_data[table] = table_rows
            total_rows_backed_up += len(table_rows)

            print(f"Backed up table '{table}': {len(table_rows)} rows")

    # Write JSON backup
    with open(json_backup_file, "w", encoding="utf-8") as f:
        json.dump(full_data, f, cls=CustomEncoder, indent=2)

    print(f"\nSuccessfully wrote JSON backup to: {json_backup_file}")
    print(f"Total tables: {len(tables)}, Total rows: {total_rows_backed_up}")
    return json_backup_file


if __name__ == "__main__":
    backup_local_database()
