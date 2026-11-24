"""Tests for the numpy playback synthesizer."""

import numpy as np

from hummify.config import Config
from hummify.models import Note
from hummify.playback import synthesize


def test_synthesize_returns_audio_of_expected_length() -> None:
    """Rendered duration follows beats and tempo."""
    config = Config(synth_sample_rate=8000)
    result = synthesize([Note(0, 1, 69)], 120, config)
    assert len(result) == 4000
    assert np.max(np.abs(result)) > 0
