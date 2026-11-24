"""Tests for stable frame-to-note segmentation."""

import numpy as np

from hummify.config import Config
from hummify.segment import segment_pitch_frames


def test_segment_pitch_frames_detects_sustained_pitch_change() -> None:
    """A pitch change must persist before it creates a new note."""
    times = np.arange(10) * 0.1
    pitches = np.array([60.0] * 5 + [62.0] * 5)
    notes = segment_pitch_frames(times, pitches, np.ones(10, dtype=bool), 60, Config(grid_beats=0.25))
    assert [note.midi_pitch for note in notes] == [60, 62]
    assert notes[0].start_beat == 0
    assert notes[1].start_beat == 0.5
