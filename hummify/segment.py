"""Convert pitch frames into stable monophonic note events."""

import numpy as np

from hummify.config import Config
from hummify.models import Note


def segment_pitch_frames(times: np.ndarray, midi: np.ndarray, voiced: np.ndarray, tempo_bpm: float, config: Config) -> list[Note]:
    """Detect persistent pitch changes and return notes quantized in beats."""
    if len(times) == 0 or tempo_bpm <= 0:
        return []
    hop = float(np.median(np.diff(times))) if len(times) > 1 else 0.01
    raw: list[tuple[float, float, int]] = []
    active: list[float] = []
    onset = 0.0
    candidate: list[float] = []
    for index, (value, is_voiced) in enumerate(zip(midi, voiced)):
        pitch = float(value) if is_voiced and np.isfinite(value) else None
        if pitch is None:
            if active:
                raw.append((onset, float(times[index]), int(np.rint(np.median(active)))))
            active, candidate = [], []
            continue
        if not active:
            onset, active = float(times[index]), [pitch]
            continue
        if abs(pitch - float(np.median(active))) >= config.pitch_change_semitones:
            candidate.append(pitch)
            if len(candidate) >= config.pitch_change_frames:
                boundary = float(times[index - len(candidate) + 1])
                raw.append((onset, boundary, int(np.rint(np.median(active)))))
                onset, active, candidate = boundary, candidate, []
        else:
            active.extend(candidate)
            candidate = []
            active.append(pitch)
    if active:
        raw.append((onset, float(times[-1] + hop), int(np.rint(np.median(active)))))
    raw = [event for event in raw if event[1] - event[0] >= config.minimum_note_seconds]
    beat_seconds = 60.0 / tempo_bpm
    return [Note(round(start / beat_seconds / config.grid_beats) * config.grid_beats,
                 max(config.grid_beats, round((end - start) / beat_seconds / config.grid_beats) * config.grid_beats), pitch)
            for start, end, pitch in raw]
