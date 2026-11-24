"""Configuration for pitch tracking and display."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Tunable settings used by the transcription pipeline."""

    sample_rate: int = 22050
    frame_length: int = 2048
    hop_length: int = 256
    fmin_hz: float = 65.0
    fmax_hz: float = 1000.0
    median_filter_size: int = 5
    pitch_change_semitones: float = 0.8
    pitch_change_frames: int = 3
    minimum_note_seconds: float = 0.08
    grid_beats: float = 0.25
    default_tempo_bpm: float = 100.0
    synth_sample_rate: int = 22050
