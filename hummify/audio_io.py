"""Audio loading and resampling helpers."""

import io

import librosa
import numpy as np


def load_audio(source: str | bytes, sample_rate: int) -> tuple[np.ndarray, int]:
    """Load an audio file or byte stream as mono audio at the requested rate."""
    data, rate = librosa.load(io.BytesIO(source) if isinstance(source, bytes) else source, sr=sample_rate, mono=True)
    return data.astype(np.float32), rate
