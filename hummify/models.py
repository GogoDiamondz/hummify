"""Data models for transcribed notes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    """A semitone-snapped note with timing in beats."""

    start_beat: float
    duration_beats: float
    midi_pitch: int
