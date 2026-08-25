
# K12+K13+K16 Trinity-CONTRARIAN 2026-05-17 (Cross-LLM-validated)
def k12_provenance(payload: bytes, key: bytes = b"df-trinity-contrarian-v1") -> dict:
    import hashlib, hmac
    return {
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "hmac_sha256": hmac.new(key, payload, hashlib.sha256).hexdigest(),
    }

def k13_anchor(payload_hash: str) -> dict:
    from datetime import datetime, timezone
    return {
        "anchor_type": "rfc3161-mock",
        "iso_ts": datetime.now(timezone.utc).isoformat(),
        "payload_hash": payload_hash,
    }

def k16_lock_or_exit(df_name: str):
    import fcntl, os, sys
    lock_path = f"/tmp/df-trinity-{df_name}.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        sys.exit(3)

"""All-tests for df-publishing-orchestrator. [CRUX-MK]
15+ Tests across 5 modules (audit + verlag + vg_wort + metis + orchestrator)."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.all_modules import (
    AuditLogger, GraphityVerlagConnector, VgWortTracker,
    MetisReformCompliance, PublishingOrchestrator,
    BUECHER_TRILOGIE_REGISTRY, OrchestrationResult,
    VerlagSubmission, VgWortRoyalty)


# AuditLogger Tests (3)

def test_audit_logger_append_and_verify():
    with tempfile.TemporaryDirectory() as tmp:
        log = AuditLogger(Path(tmp) / "audit.jsonl", hmac_key=b"test-key-32-bytes-long-aaaaaaaaaa")
        log.append("test_event", {"foo": "bar"})
        log.append("test_event2", {"foo": "baz"})
        assert log.verify_chain() is True


def test_audit_logger_genesis():
    with tempfile.TemporaryDirectory() as tmp:
        log = AuditLogger(Path(tmp) / "audit.jsonl")
        entry = log.append("first", {"k": "v"})
        assert entry.prev_hash == "GENESIS"
        assert entry.sequence_no == 0


def test_audit_logger_chain_continuity():
    with tempfile.TemporaryDirectory() as tmp:
        log = AuditLogger(Path(tmp) / "audit.jsonl")
        e1 = log.append("a", {})
        e2 = log.append("b", {})
        assert e2.prev_hash == e1.chain_hash
        assert e2.sequence_no == 1


# GraphityVerlagConnector Tests (3)

def test_verlag_connector_default_mock():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("DF_PUBLISHING_REAL_ENABLED", None)
        c = GraphityVerlagConnector()
        assert c._check_real_mode() is False


def test_verlag_submit_mock():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("DF_PUBLISHING_REAL_ENABLED", None)
        c = GraphityVerlagConnector()
        sub = c.submit_book("Test Book", 10)
        assert sub.source == "mock"
        assert sub.book_title == "Test Book"
        assert sub.status == "submitted"


def test_verlag_real_without_ticket_raises():
    with patch.dict(os.environ, {"DF_PUBLISHING_REAL_ENABLED": "true"}, clear=False):
        os.environ.pop("PHRONESIS_TICKET", None)
        c = GraphityVerlagConnector()
        try:
            c.submit_book("X", 5)
            raise AssertionError("Should raise")
        except RuntimeError as e:
            assert "PHRONESIS_TICKET" in str(e)


# VgWortTracker Tests (3)

def test_vg_wort_eligible_above_min():
    t = VgWortTracker()
    royalty = t.estimate_royalty("Test", 50000)
    assert royalty.metis_compliant is True
    assert royalty.estimated_eur > 0


def test_vg_wort_below_min_returns_zero():
    t = VgWortTracker()
    royalty = t.estimate_royalty("Tiny", 500)
    assert royalty.metis_compliant is False
    assert royalty.estimated_eur == 0.0


def test_vg_wort_calculation():
    t = VgWortTracker()
    royalty = t.estimate_royalty("Book", 10000)
    # 10000 / 1000 * 4.50 = 45.00 EUR
    assert royalty.estimated_eur == 45.0


# MetisReformCompliance Tests (3)

def test_metis_complete_metadata_passes():
    m = MetisReformCompliance()
    meta = {
        "book_title": "Test",
        "author": "Martin",
        "isbn": "978-X",
        "word_count": 100000,
        "publication_date": "2026-01-01",
    }
    ok, issues = m.check(meta)
    assert ok is True
    assert len(issues) == 0


def test_metis_missing_field_fails():
    m = MetisReformCompliance()
    meta = {"book_title": "Test", "word_count": 100000}
    ok, issues = m.check(meta)
    assert ok is False
    assert any("missing_required_field:author" in i for i in issues)


def test_metis_below_min_words_fails():
    m = MetisReformCompliance()
    meta = {
        "book_title": "Tiny", "author": "M",
        "isbn": "X", "word_count": 1000, "publication_date": "X",
    }
    ok, issues = m.check(meta)
    assert ok is False
    assert any("word_count_below_metis_minimum" in i for i in issues)


# PublishingOrchestrator Tests (4)

def test_orchestrator_init():
    with tempfile.TemporaryDirectory() as tmp:
        o = PublishingOrchestrator(audit_log_dir=Path(tmp))
        assert o.book_count() == 4


def test_orchestrator_books_registry():
    with tempfile.TemporaryDirectory() as tmp:
        o = PublishingOrchestrator(audit_log_dir=Path(tmp))
        books = o.list_books()
        titles = [b["title"] for b in books]
        assert "Symbiotic Minds" in titles
        assert "AI Leadership" in titles
        assert "Mathematik der Macht" in titles
        assert "Die Souveraene Maschine" in titles


def test_orchestrator_total_words():
    with tempfile.TemporaryDirectory() as tmp:
        o = PublishingOrchestrator(audit_log_dir=Path(tmp))
        # 14*8000 + 12*6000 + 16*9000 + 10*7000 = 112000 + 72000 + 144000 + 70000 = 398000
        assert o.total_words_all_books() == 398000


def test_orchestrator_process_all_books_mock():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DF_PUBLISHING_REAL_ENABLED", None)
            o = PublishingOrchestrator(audit_log_dir=Path(tmp))
            result = o.process_all_books()
            assert result.books_processed == 4
            assert result.submissions_count == 4
            assert result.source_mode == "mock"
            assert result.royalty_estimates_eur_total > 0
