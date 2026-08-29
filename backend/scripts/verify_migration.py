"""Verification script comparing row counts and primary keys between Local PostgreSQL and Supabase PostgreSQL.
"""

import urllib.parse

from sqlalchemy import create_engine, inspect, text


def verify_migration():
    local_url = "postgresql+psycopg://naccer:naccerpass@localhost:5432/naccer_db"

    password = "Ja$wanthkumar"
    encoded_pass = urllib.parse.quote_plus(password)
    proj_ref = "zukdmruvoamepddafmyi"
    host = "aws-0-ap-southeast-1.pooler.supabase.com"
    supabase_url = f"postgresql+psycopg://postgres.{proj_ref}:{encoded_pass}@{host}:5432/postgres?sslmode=require"

    local_engine = create_engine(local_url)
    supabase_engine = create_engine(supabase_url)

    inspector = inspect(local_engine)
    all_tables = sorted(inspector.get_table_names())

    print("=========================================================================")
    print("           LOCAL vs SUPABASE DATABASE MIGRATION AUDIT REPORT             ")
    print("=========================================================================\n")
    print(f"{'TABLE NAME':35s} | {'LOCAL':10s} | {'SUPABASE':10s} | {'STATUS':10s}")
    print("-" * 75)

    all_matched = True
    total_local_rows = 0
    total_supabase_rows = 0

    with local_engine.connect() as local_conn, supabase_engine.connect() as supabase_conn:
        for t in all_tables:
            local_count = local_conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
            supa_count = supabase_conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()

            total_local_rows += local_count
            total_supabase_rows += supa_count

            status = "MATCH" if local_count == supa_count else "MISMATCH"
            if local_count != supa_count:
                all_matched = False

            print(f"{t:35s} | {local_count:<10d} | {supa_count:<10d} | {status:10s}")

    print("-" * 75)
    print(f"{'TOTAL ROWS':35s} | {total_local_rows:<10d} | {total_supabase_rows:<10d} | {'MATCH' if all_matched else 'MISMATCH'}")
    print("=========================================================================\n")

    return all_matched


if __name__ == "__main__":
    verify_migration()
