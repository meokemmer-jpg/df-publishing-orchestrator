"""Die Publikations-Sperre muss WIRKEN, nicht nur dastehen. [CRUX-MK]

Hintergrund: Am 10.09.2026 wurde die Sperre als Kommentar eingetragen und die Schleife
lief unveraendert ueber alle vier Buecher weiter — Deklaration ohne Wirkung. Dieser Test
faellt, sobald das wieder passiert.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from all_modules import PublishingOrchestrator, BUECHER_TRILOGIE_REGISTRY


def test_gesperrtes_buch_wird_nicht_eingereicht(tmp_path):
    o = PublishingOrchestrator()
    r = o.process_all_books()
    gesperrt = [b for b in BUECHER_TRILOGIE_REGISTRY if b.get("publication_blocked")]
    assert gesperrt, "Testvoraussetzung: mindestens ein Buch ist gesperrt"
    # NEGATIV: die Zahl verarbeiteter Buecher liegt unter der Gesamtzahl
    assert r.books_processed == len(BUECHER_TRILOGIE_REGISTRY) - len(gesperrt), (
        f"Sperre wirkungslos: {r.books_processed} verarbeitet, "
        f"erwartet {len(BUECHER_TRILOGIE_REGISTRY) - len(gesperrt)}")


def test_sperre_wird_protokolliert():
    o = PublishingOrchestrator()
    o.process_all_books()
    eintraege = pathlib.Path(o.audit.log_path).read_text(errors="replace")
    assert "book_publication_blocked" in eintraege, "Sperre ohne Audit-Eintrag"
    assert "mathematik-der-macht" in eintraege
