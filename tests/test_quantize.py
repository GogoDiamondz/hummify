"""Tests for timing quantization."""

from hummify.config import Config
from hummify.models import Note
from hummify.quantize import quantize_notes


def test_quantize_notes_snaps_onsets_and_lengths() -> None:
    """Beat positions round to the configured grid."""
    result = quantize_notes([Note(0.37, 0.62, 64)], 100, Config(grid_beats=0.25))
    assert result == [Note(0.25, 0.5, 64)]
