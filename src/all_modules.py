"""All-Modules consolidated for df-publishing-orchestrator (Welle-44 Skeleton). [CRUX-MK]

Lambda-Honesty-Caveat:
- GraphityVerlagConnector ist STUB (kein Real-API-Call in Skeleton)
- VgWortTracker ist STUB (METIS-Reform-Compliance ohne Real-Submission)
- Mock-Default fuer alle 4 Sub-Modules
- Real-Mode (DF_PUBLISHING_REAL_ENABLED=true) erfordert PHRONESIS_TICKET + raises NotImplementedError
"""

import os
import sys
import json
import hmac
import hashlib
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# AUDIT LOGGER
# ============================================================

@dataclass
class AuditEntry:
    iso_timestamp: str
    event_type: str
    payload: Dict
    sequence_no: int
    prev_hash: str
    chain_hash: str = ""


class AuditLogger:
    def __init__(self, log_path: Path, hmac_key: Optional[bytes] = None):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._hmac_key = hmac_key or os.urandom(32)
        self._lock = threading.Lock()
        self._sequence_no = 0
        self._last_hash = "GENESIS"
        if self.log_path.exists():
            self._recover_state()

    def _recover_state(self):
        with self.log_path.open("r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    self._sequence_no = entry["sequence_no"] + 1
                    self._last_hash = entry["chain_hash"]
                except (json.JSONDecodeError, KeyError):
                    continue

    def _compute_chain_hash(self, prev_hash: str, payload_json: str) -> str:
        msg = (prev_hash + payload_json).encode("utf-8")
        return hmac.new(self._hmac_key, msg, hashlib.sha256).hexdigest()

    def append(self, event_type: str, payload: Dict) -> AuditEntry:
        with self._lock:
            payload_json = json.dumps(payload, sort_keys=True)
            chain_hash = self._compute_chain_hash(self._last_hash, payload_json)
            entry = AuditEntry(
                iso_timestamp=_iso_now(), event_type=event_type, payload=payload,
                sequence_no=self._sequence_no, prev_hash=self._last_hash,
                chain_hash=chain_hash)
            with self.log_path.open("a") as f:
                f.write(json.dumps({
                    "iso_timestamp": entry.iso_timestamp,
                    "event_type": entry.event_type,
                    "payload": entry.payload,
                    "sequence_no": entry.sequence_no,
                    "prev_hash": entry.prev_hash,
                    "chain_hash": entry.chain_hash,
                }) + "\n")
            self._sequence_no += 1
            self._last_hash = chain_hash
            return entry

    def verify_chain(self) -> bool:
        if not self.log_path.exists():
            return True
        prev_hash = "GENESIS"
        with self.log_path.open("r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    payload_json = json.dumps(entry["payload"], sort_keys=True)
                    expected = self._compute_chain_hash(prev_hash, payload_json)
                    if expected != entry["chain_hash"] or entry["prev_hash"] != prev_hash:
                        return False
                    prev_hash = entry["chain_hash"]
                except (json.JSONDecodeError, KeyError):
                    return False
        return True


# ============================================================
# GRAPHITY VERLAG CONNECTOR (Stub)
# ============================================================

@dataclass
class VerlagSubmission:
    book_title: str
    chapter_count: int
    submission_id: str
    iso_timestamp: str
    source: str  # "mock" | "real-api" | "stub"
    status: str  # "submitted" | "rejected" | "accepted"


class GraphityVerlagConnector:
    """Stub-Connector zu Graphity-Verlag. Mock-Default per ENV-Var-Gate."""

    def __init__(self):
        pass

    def _check_real_mode(self) -> bool:
        return os.environ.get("DF_PUBLISHING_REAL_ENABLED", "false") == "true"

    def _phronesis_ticket(self) -> Optional[str]:
        ticket = os.environ.get("PHRONESIS_TICKET", "")
        return ticket if ticket else None

    def submit_book(self, book_title: str, chapter_count: int) -> VerlagSubmission:
        if self._check_real_mode():
            ticket = self._phronesis_ticket()
            if not ticket:
                raise RuntimeError(
                    "Real-Mode erfordert PHRONESIS_TICKET. "
                    "Phronesis-Pflicht Martin: K_0/Q_0-Approval.")
            raise NotImplementedError(
                f"Real-API-Submission ist Welle-45+-Pflicht. Ticket: {ticket}")

        # Mock-Submission
        submission_id = f"MOCK-{book_title.replace(' ', '-')}-{int(datetime.now().timestamp())}"
        return VerlagSubmission(
            book_title=book_title, chapter_count=chapter_count,
            submission_id=submission_id, iso_timestamp=_iso_now(),
            source="mock", status="submitted")


# ============================================================
# VG-WORT TRACKER (Stub mit METIS-Reform-Compliance)
# ============================================================

@dataclass
class VgWortRoyalty:
    book_title: str
    word_count: int
    estimated_eur: float
    iso_timestamp: str
    source: str  # "mock" | "real" | "stub"
    metis_compliant: bool


class VgWortTracker:
    """VG-Wort-Royalty-Tracking. METIS-Reform 2026+ ready."""

    # METIS-Reform-Schwellenwerte (vereinfacht)
    METIS_MIN_WORDS_PROSE = 1800  # min words for prose-eligible
    EUR_PER_1000_WORDS_PROSE = 4.50  # geschaetzt, METIS-Phase

    def __init__(self):
        pass

    def _check_real_mode(self) -> bool:
        return os.environ.get("DF_PUBLISHING_REAL_ENABLED", "false") == "true"

    def estimate_royalty(self, book_title: str, total_words: int) -> VgWortRoyalty:
        """Mock-Estimate fuer VG-Wort-Royalty."""
        metis_ok = total_words >= self.METIS_MIN_WORDS_PROSE
        eur = (total_words / 1000.0) * self.EUR_PER_1000_WORDS_PROSE if metis_ok else 0.0
        return VgWortRoyalty(
            book_title=book_title, word_count=total_words,
            estimated_eur=eur, iso_timestamp=_iso_now(),
            source="mock" if not self._check_real_mode() else "stub",
            metis_compliant=metis_ok)


# ============================================================
# METIS REFORM COMPLIANCE
# ============================================================

class MetisReformCompliance:
    """Compliance-Checker fuer METIS-Reform 2026+ (vereinfacht)."""

    REQUIRED_FIELDS = ["book_title", "author", "isbn", "word_count", "publication_date"]
    MIN_WORDS_BOOK = 50000  # METIS-Minimum fuer Buch-Status

    def check(self, book_metadata: Dict) -> Tuple[bool, List[str]]:
        """Returns (passes, list_of_issues)."""
        issues = []

        for field_name in self.REQUIRED_FIELDS:
            if field_name not in book_metadata or not book_metadata[field_name]:
                issues.append(f"missing_required_field:{field_name}")

        word_count = book_metadata.get("word_count", 0)
        if word_count < self.MIN_WORDS_BOOK:
            issues.append(f"word_count_below_metis_minimum:{word_count}<{self.MIN_WORDS_BOOK}")

        return len(issues) == 0, issues


# ============================================================
# PUBLISHING ORCHESTRATOR
# ============================================================

@dataclass
class OrchestrationResult:
    iso_started: str
    iso_completed: str
    books_processed: int
    submissions_count: int
    royalty_estimates_eur_total: float
    metis_failures: int
    source_mode: str
    audit_log_path: str


# 4 Books (Source-of-Truth fuer Cross-Book-Coordination)
BUECHER_TRILOGIE_REGISTRY: List[Dict] = [
    {"id": "symbiotic-minds", "title": "Symbiotic Minds",
     "subtitle": "Mensch-AI-Symbiose", "chapters": 14, "words_per_chapter": 8000},
    {"id": "ai-leadership", "title": "AI Leadership",
     "subtitle": "Fuehrung in AI-First-Unternehmen", "chapters": 12, "words_per_chapter": 6000},
    {"id": "mathematik-der-macht", "title": "Mathematik der Macht",
     "subtitle": "Hamilton-Optimierung", "chapters": 16, "words_per_chapter": 9000},
    {"id": "souveraene-maschine", "title": "Die Souveraene Maschine",
     "subtitle": "K_0-AI als Werkzeug", "chapters": 10, "words_per_chapter": 7000},
]


class PublishingOrchestrator:
    """Coordinates 4 Buecher-Trilogie-Foundation-DFs."""

    def __init__(self, audit_log_dir: Optional[Path] = None):
        self.verlag = GraphityVerlagConnector()
        self.vg_wort = VgWortTracker()
        self.metis = MetisReformCompliance()
        log_dir = Path(audit_log_dir) if audit_log_dir else Path.home() / ".df-state"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.audit = AuditLogger(log_dir / "df-publishing-orchestrator-audit.jsonl")
        self.books: List[Dict] = list(BUECHER_TRILOGIE_REGISTRY)

    def _check_stop_flag(self) -> bool:
        return (Path.home() / ".df-state" / "df-publishing-orchestrator.STOP.flag").exists()

    def _detect_source_mode(self) -> str:
        return "real" if os.environ.get("DF_PUBLISHING_REAL_ENABLED", "false") == "true" else "mock"

    def list_books(self) -> List[Dict]:
        return list(self.books)

    def book_count(self) -> int:
        return len(self.books)

    def total_words_all_books(self) -> int:
        return sum(b["chapters"] * b["words_per_chapter"] for b in self.books)

    def process_all_books(self) -> OrchestrationResult:
        """Hauptmethode: orchestriere Submission + Royalty-Estimate fuer alle 4 Buecher."""
        iso_start = _iso_now()
        source_mode = self._detect_source_mode()

        self.audit.append("orchestration_start", {
            "iso_timestamp": iso_start, "source_mode": source_mode,
            "books_count": self.book_count()})

        if self._check_stop_flag():
            self.audit.append("orchestration_stopped", {"reason": "STOP.flag detected"})
            return OrchestrationResult(
                iso_started=iso_start, iso_completed=_iso_now(),
                books_processed=0, submissions_count=0,
                royalty_estimates_eur_total=0.0, metis_failures=0,
                source_mode=source_mode, audit_log_path=str(self.audit.log_path))

        submissions, royalty_total, metis_failures = 0, 0.0, 0

        for book in self.books:
            total_words = book["chapters"] * book["words_per_chapter"]
            book_meta = {
                "book_title": book["title"],
                "author": "Martin Kemmer",
                "isbn": "TBD",
                "word_count": total_words,
                "publication_date": "TBD-2027",
            }

            # METIS-Compliance-Check
            metis_ok, issues = self.metis.check(book_meta)
            if not metis_ok:
                self.audit.append("metis_compliance_failed", {
                    "book": book["title"], "issues": issues})
                metis_failures += 1

            # Submit zu Verlag (Mock-Default)
            try:
                submission = self.verlag.submit_book(book["title"], book["chapters"])
                self.audit.append("verlag_submission", {
                    "book": book["title"], "submission_id": submission.submission_id,
                    "source": submission.source})
                submissions += 1
            except (RuntimeError, NotImplementedError) as e:
                self.audit.append("verlag_submission_failed", {
                    "book": book["title"], "error": str(e)})

            # VG-Wort-Royalty-Estimate
            royalty = self.vg_wort.estimate_royalty(book["title"], total_words)
            self.audit.append("vg_wort_estimate", {
                "book": book["title"], "estimated_eur": royalty.estimated_eur,
                "metis_compliant": royalty.metis_compliant})
            royalty_total += royalty.estimated_eur

        self.audit.append("orchestration_complete", {
            "books_processed": len(self.books),
            "submissions": submissions,
            "royalty_total_eur": royalty_total,
            "metis_failures": metis_failures})

        return OrchestrationResult(
            iso_started=iso_start, iso_completed=_iso_now(),
            books_processed=len(self.books), submissions_count=submissions,
            royalty_estimates_eur_total=royalty_total,
            metis_failures=metis_failures,
            source_mode=source_mode, audit_log_path=str(self.audit.log_path))


def main():
    orch = PublishingOrchestrator()
    result = orch.process_all_books()
    print(f"DF-publishing-orchestrator run: {result.books_processed} books, "
          f"{result.submissions_count} submissions, "
          f"royalty-est EUR {result.royalty_estimates_eur_total:.2f}, "
          f"mode={result.source_mode}")
    sys.exit(0)


if __name__ == "__main__":
    main()
