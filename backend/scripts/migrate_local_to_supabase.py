"""Data migration script copying all records from local PostgreSQL to Supabase PostgreSQL.

Preserves exact primary keys, foreign keys, timestamps, UUIDs, floats, JSON objects, and NULL values.
Handles proper table order based on foreign key dependencies.
"""

import json
import urllib.parse
from typing import Any

from sqlalchemy import create_engine, text


def serialize_json_fields(row: dict[str, Any]) -> dict[str, Any]:
    cleaned = {}
    for k, v in row.items():
        if isinstance(v, (list, dict)):
            cleaned[k] = json.dumps(v)
        else:
            cleaned[k] = v
    return cleaned


def migrate_data():
    local_url = "postgresql+psycopg://naccer:naccerpass@localhost:5432/naccer_db"

    password = "Ja$wanthkumar"
    encoded_pass = urllib.parse.quote_plus(password)
    proj_ref = "zukdmruvoamepddafmyi"
    host = "aws-0-ap-southeast-1.pooler.supabase.com"
    supabase_url = f"postgresql+psycopg://postgres.{proj_ref}:{encoded_pass}@{host}:5432/postgres?sslmode=require"

    local_engine = create_engine(local_url)
    supabase_engine = create_engine(supabase_url)

    # Dependency-ordered tables
    table_order = [
        "alembic_version",
        "institutions",
        "proposals",
        "documents",
        "document_pages",
        "proposal_sections",
        "import_batches",
        "historical_projects",
        "historical_project_embeddings",
        "historical_source_documents",
        "research_papers",
        "paper_pages",
        "scientific_evidences",
        "evaluation_rubrics",
        "rubric_criteria",
        "evaluations",
        "evaluation_criteria",
        "evaluation_evidences",
        "ai_analyses",
        "evaluation_decision_packs",
        "evaluation_assignments",
        "reviewer_conflict_declarations",
        "audit_events",
        "evaluation_audit_events",
        "review_comments",
        "financial_checks",
        "evidences",
    ]

    print("Starting data migration from Local PostgreSQL -> Supabase PostgreSQL...\n")

    with local_engine.connect() as local_conn, supabase_engine.connect() as supabase_conn:
        for table in table_order:
            # 1. Fetch rows from local
            rows = local_conn.execute(text(f'SELECT * FROM "{table}"')).mappings().all()

            if not rows:
                print(f"Table '{table:32s}': 0 local rows (skipped)")
                continue

            # Convert RowMapping items to dict and format JSON fields
            dict_rows = [serialize_json_fields(dict(r)) for r in rows]

            # 2. Get column names
            col_names = list(dict_rows[0].keys())
            cols_str = ", ".join([f'"{c}"' for c in col_names])
            vals_str = ", ".join([f":{c}" for c in col_names])

            # Prepare insert statement with ON CONFLICT DO NOTHING to allow safe re-runs
            insert_stmt = text(f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str}) ON CONFLICT DO NOTHING')

            # 3. Execute row-by-row or batch insert into Supabase
            try:
                supabase_conn.execute(insert_stmt, dict_rows)
                supabase_conn.commit()
                print(f"Table '{table:32s}': Copied {len(dict_rows)} rows to Supabase [SUCCESS]")
            except Exception as err:
                print(f"Batch failed for '{table}', retrying row-by-row: {err}")
                supabase_conn.rollback()
                copied_count = 0
                for r in dict_rows:
                    try:
                        supabase_conn.execute(insert_stmt, [r])
                        supabase_conn.commit()
                        copied_count += 1
                    except Exception as r_err:
                        print(f"  Failed row in '{table}': {r_err}")
                print(f"Table '{table:32s}': Copied {copied_count}/{len(dict_rows)} rows row-by-row")

    print("\nData migration completed successfully!")


if __name__ == "__main__":
    migrate_data()
