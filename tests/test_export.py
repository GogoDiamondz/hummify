"""Tests for MIDI serialization."""

import io

import pretty_midi

from hummify.export import notes_to_midi
from hummify.models import Note


def test_notes_to_midi_serializes_beat_timing() -> None:
    """A one-beat note at 120 BPM becomes a half-second MIDI note."""
    data = notes_to_midi([Note(1, 1, 69)], 120)
    midi = pretty_midi.PrettyMIDI(io.BytesIO(data))
    note = midi.instruments[0].notes[0]
    assert note.pitch == 69
    assert abs(note.start - 0.5) < 0.01
    assert abs(note.end - 1.0) < 0.01
