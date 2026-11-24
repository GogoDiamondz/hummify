"""Render note sequences to audio using a numpy sine synth."""

import numpy as np

from hummify.config import Config
from hummify.models import Note


def synthesize(notes: list[Note], tempo_bpm: float, config: Config) -> np.ndarray:
    """Render beat-timed notes as a mono audio array."""
    rate = config.synth_sample_rate
    total = max((n.start_beat + n.duration_beats for n in notes), default=0.0) * 60.0 / tempo_bpm
    audio = np.zeros(int(np.ceil(total * rate)), dtype=np.float32)
    for note in notes:
        start = int(note.start_beat * 60.0 / tempo_bpm * rate)
        length = min(int(note.duration_beats * 60.0 / tempo_bpm * rate), len(audio) - start)
        if length <= 0:
            continue
        time = np.arange(length) / rate
        freq = 440.0 * 2.0 ** ((note.midi_pitch - 69) / 12.0)
        envelope = np.minimum(1.0, np.arange(length) / max(1, int(0.01 * rate)))
        audio[start:start + length] += (0.25 * envelope * np.sin(2 * np.pi * freq * time)).astype(np.float32)
    return np.clip(audio, -1.0, 1.0)
