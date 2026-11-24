"""Tests for pitch conversion."""

import numpy as np

from hummify.pitch import hz_to_midi


def test_hz_to_midi_converts_standard_pitches_and_silence() -> None:
    """A4 maps to MIDI 69 and silence remains undefined."""
    result = hz_to_midi(np.array([440.0, 0.0]))
    assert result[0] == 69.0
    assert np.isnan(result[1])

