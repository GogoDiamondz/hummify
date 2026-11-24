"""Tests for transcription evaluation metrics."""

from hummify.evaluate import score_notes
from hummify.models import Note


def test_score_notes_perfect_match() -> None:
    """Matching synthetic notes receive perfect scores."""
    notes = [Note(0, 1, 60), Note(1, 0.5, 64)]
    scores = score_notes(notes, notes, tempo_bpm=120)
    assert scores["f1"] == 1.0
    assert scores["onset_only_f1"] == 1.0


def test_score_notes_empty_estimate_has_zero_recall() -> None:
    """An empty estimate cannot match reference notes."""
    scores = score_notes([Note(0, 1, 60)], [], tempo_bpm=120)
    assert scores["recall"] == 0.0
    assert scores["f1"] == 0.0
