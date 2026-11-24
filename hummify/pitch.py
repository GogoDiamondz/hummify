"""Frame-wise pitch tracking and semitone conversion."""

import numpy as np

from hummify.config import Config


def hz_to_midi(frequencies: np.ndarray) -> np.ndarray:
    """Convert positive frequencies in hertz to fractional MIDI pitches."""
    values = np.asarray(frequencies, dtype=float)
    result = np.full(values.shape, np.nan)
    valid = values > 0
    result[valid] = 69.0 + 12.0 * np.log2(values[valid] / 440.0)
    return result


def track_pitch(audio: np.ndarray, sample_rate: int, config: Config) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return frame times, median-filtered fractional MIDI pitches, and voiced flags."""
    import librosa

    f0, voiced, _ = librosa.pyin(
        audio, fmin=config.fmin_hz, fmax=config.fmax_hz, sr=sample_rate,
        frame_length=config.frame_length, hop_length=config.hop_length,
    )
    midi = hz_to_midi(f0)
    if config.median_filter_size > 1:
        from scipy.ndimage import median_filter

        finite = np.isfinite(midi)
        filled = np.where(finite, midi, 0.0)
        smoothed = median_filter(filled, size=config.median_filter_size, mode="nearest")
        midi = np.where(finite, smoothed, np.nan)
    times = librosa.frames_to_time(np.arange(len(f0)), sr=sample_rate, hop_length=config.hop_length)
    return times, midi, np.asarray(voiced, dtype=bool)
