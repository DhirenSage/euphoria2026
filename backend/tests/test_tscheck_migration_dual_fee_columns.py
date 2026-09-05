"""Backend coverage for CodeIgniter legacy-price migration safety.

Criterion: "Legacy prices migrate safely" -- migration 000006 adds both
sageian_fee and non_sageian_fee columns to `events` and copies every existing
event's legacy `fee` into both fields; fresh seed data also populates both
fields (never leaving either column at 0 while `fee` is non-zero).

Runs directly against the euphoria_release MySQL database (127.0.0.1:3307),
per the briefing's seed_facts, and inspects the migration source under
/app/codeigniter for the copy-both-fields behaviour.
"""
from pathlib import Path

import pymysql
import pytest

MIGRATION_PATH = Path(
    "/app/codeigniter/app/Database/Migrations/2026-01-01-000006_AddAffiliationFees.php"
)


def db_conn():
    return pymysql.connect(
        host="127.0.0.1", port=3307, user="root", password="",
        database="euphoria_release", cursorclass=pymysql.cursors.DictCursor,
    )


def test_events_table_has_both_affiliation_fee_columns():
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("show columns from events like 'sageian_fee'")
            sageian_col = cur.fetchone()
            cur.execute("show columns from events like 'non_sageian_fee'")
            non_sageian_col = cur.fetchone()
    assert sageian_col is not None, "events.sageian_fee column is missing"
    assert non_sageian_col is not None, "events.non_sageian_fee column is missing"


def test_every_priced_event_has_non_zero_affiliation_fees_matching_or_derived_from_legacy_fee():
    """Every existing paid event (fee > 0) must have both sageian_fee and
    non_sageian_fee populated (non-zero) -- proving the legacy fee value was
    copied into both fields rather than left at the column default of 0."""
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id, name, fee, sageian_fee, non_sageian_fee from events where fee > 0")
            rows = cur.fetchall()
    assert rows, "expected at least one priced event in euphoria_release.events"
    unmigrated = [
        r for r in rows
        if float(r["sageian_fee"]) == 0.0 or float(r["non_sageian_fee"]) == 0.0
    ]
    assert not unmigrated, (
        f"found priced events with an unmigrated (zero) affiliation fee: "
        f"{[(r['id'], r['name'], r['fee'], r['sageian_fee'], r['non_sageian_fee']) for r in unmigrated]}"
    )


def test_dance_competition_fixture_has_distinct_documented_fees():
    """seed_facts: Dance Competition is configured as SAGEian 100 / Non-SAGEian 250."""
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select sageian_fee, non_sageian_fee from events where slug='dance-competition'")
            row = cur.fetchone()
    assert row, "dance-competition event not found"
    assert float(row["sageian_fee"]) == 100.0
    assert float(row["non_sageian_fee"]) == 250.0


def test_migration_source_copies_legacy_fee_into_both_affiliation_columns():
    """Static check on the migration file itself: it must add both columns and
    copy the legacy `fee` value into both, rather than dropping/losing existing
    prices."""
    assert MIGRATION_PATH.exists(), f"migration file not found at {MIGRATION_PATH}"
    source = MIGRATION_PATH.read_text()
    assert "sageian_fee" in source and "non_sageian_fee" in source, (
        "migration does not reference both affiliation fee columns"
    )
    assert "SET sageian_fee = fee, non_sageian_fee = fee" in source, (
        "migration does not copy the legacy fee into both affiliation columns"
    )
