"""Snap note pitches and durations to the configured beat grid."""

from hummify.config import Config
from hummify.models import Note


def quantize_notes(notes: list[Note], tempo_bpm: float, config: Config) -> list[Note]:
    """Snap note onsets and durations to a fixed beat grid."""
    if tempo_bpm <= 0:
        raise ValueError("tempo_bpm must be positive")
    return [Note(round(n.start_beat / config.grid_beats) * config.grid_beats,
                 max(config.grid_beats, round(n.duration_beats / config.grid_beats) * config.grid_beats), n.midi_pitch)
            for n in notes]
