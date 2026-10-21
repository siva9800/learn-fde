"""The reporting copy: read-only, signed off per column, bounded, and never written."""

from __future__ import annotations

import sqlite3

import pytest

from godavari_integration import synth_sources as ss
from godavari_integration.reporting import QueryRefused, ReportingReader


@pytest.fixture(scope="module")
def db(tmp_path_factory, facts):
    return ss.build_reporting_db(tmp_path_factory.mktemp("rpt") / "reporting.sqlite", facts, ss.production_status(facts))


def test_signed_off_columns_can_be_read(db):
    r = ReportingReader(db)
    rows = r.query("SELECT APPL_STAT, COUNT(*) AS n FROM APPL_MST GROUP BY APPL_STAT", purpose="status mix")
    assert {x["APPL_STAT"] for x in rows} == {"A", "B", "K", "Q"}
    assert r.last_refresh().isoformat() == "2026-11-13T05:00:00"


@pytest.mark.parametrize("sql", ["SELECT APPL_NM FROM APPL_MST", "SELECT * FROM APPL_MST",
                                 "SELECT FILE_NO FROM APPL_MST WHERE PAN_NO LIKE 'A%'",
                                 "SELECT PHONE_NO FROM BRANCH_MST"])
def test_identifiers_and_unsigned_columns_are_denied_by_the_authorizer(db, sql):
    with pytest.raises(QueryRefused, match="prohibited"):
        ReportingReader(db).query(sql, purpose="test")


@pytest.mark.parametrize("sql", ["UPDATE APPL_MST SET APPL_STAT = 'K'", "DELETE FROM CODE_MST",
                                 "INSERT INTO CODE_MST VALUES ('a', 'b', 'c', 'Y')", "DROP TABLE CODE_MST"])
def test_every_write_is_refused(db, sql):
    with pytest.raises(QueryRefused):
        ReportingReader(db).query(sql, purpose="test")


def test_read_only_holds_even_without_our_authorizer(db):
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        conn.execute("DELETE FROM CODE_MST")


def test_queries_are_bounded_by_rows_and_by_work(db):
    with pytest.raises(QueryRefused, match="more than 3 rows"):
        ReportingReader(db, row_cap=3).query("SELECT FILE_NO FROM FILE_REG", purpose="test")
    with pytest.raises(QueryRefused, match="interrupted"):
        ReportingReader(db).query("SELECT COUNT(*) FROM APPL_STAT_HIST a, APPL_STAT_HIST b, APPL_STAT_HIST c, "
                                  "CODE_MST d", purpose="runaway join")


def test_every_query_states_its_purpose_and_is_logged(db):
    r = ReportingReader(db)
    with pytest.raises(QueryRefused, match="purpose"):
        r.query("SELECT 1", purpose=" ")
    r.query("SELECT COUNT(*) AS n FROM FILE_REG", purpose="files registered")
    assert r.log.entries[-1][0] == "files registered"
