# Copilot Instructions

Hummify is a Python class project. A user hums a melody; the app transcribes it into notes (pitch and duration), plays them back, and exports MIDI. Sheet music (MusicXML) and note editing come in a later phase.

**Current phase:** 1 (basic prototype: record or upload, pYIN, semitone snapping, list of notes). Do not build later-phase features unless asked. Update this line as phases finish.

## Stack

Python 3.11+, Streamlit (UI), `librosa` (pYIN pitch tracking), `numpy`, `soundfile`, `pretty_midi` (MIDI), `music21` (key detection, MusicXML), `mir_eval` (evaluation), `pytest`. Prefer these over new dependencies.

## Project layout

- `app.py`: Streamlit UI only, no algorithm logic.
- `hum2notes/config.py`: all tunable thresholds in one `Config` dataclass.
- `hum2notes/models.py`: `Note` dataclass (`start_beat`, `duration_beats`, `midi_pitch`).
- `hum2notes/audio_io.py`: load, record, resample.
- `hum2notes/pitch.py`: audio to per-frame frequency and voiced flag.
- `hum2notes/segment.py`: frames to raw notes.
- `hum2notes/quantize.py`: snap pitch and timing.
- `hum2notes/export.py`: notes to MIDI or MusicXML.
- `hum2notes/playback.py`: notes to audio (numpy synth by default).
- `hum2notes/evaluate.py`: score output against ground truth.
- `tests/`: one test file per module.
- `data/test_recordings/`: test clips with ground-truth notes (never overwrite).

## Rules to follow when suggesting code

1. Pipeline stages are pure functions: arrays or dataclasses in, arrays or dataclasses out. No file access, globals, or Streamlit calls in `pitch`, `segment`, `quantize`, `export`, `playback`, or `evaluate`.
2. Never hard-code thresholds (semitone tolerance, minimum note length, filter size, grid resolution). Read them from `Config`.
3. Pitch is fractional MIDI note numbers internally. Convert from Hz once, in `pitch.py`. After quantization, time is in beats, not seconds.
4. Pipeline order: `audio_io` -> `pitch` -> `segment` -> `quantize` -> notes -> export, playback, or UI.
5. Playback must work with the numpy synth alone. FluidSynth is optional.
6. Add type hints and a short docstring to every public function.
7. Keep functions small. No debug prints or commented-out code.

## Algorithm reminders

- Apply a median filter to the pitch track to remove octave errors and smooth vibrato.
- Start a new note when pitch moves about 0.7 to 1 semitone from the running median and holds for a minimum number of frames, or when the signal goes unvoiced or energy dips. Merge notes shorter than about 80 ms into neighbors.
- Quantize timing to a sixteenth-note grid using the metronome click tempo, falling back to a user-entered tempo.
- Key snapping is optional and off by default.

## Tests

- Use standard `pytest` or Python's built-in `unittest`; do not add or rely on BYU-specific tools or plugins.
- Write or update a pytest test for every function you change.
- Use synthetic audio (generated tones with known pitch and length) in unit tests, not recordings.
- Evaluation uses `mir_eval.transcription` with 50 ms onset and 50 cent pitch tolerance. Report precision, recall, and F1.

## Commands

```
pip install -r requirements.txt
streamlit run app.py
pytest
python -m hum2notes.evaluate data/test_recordings
```

## Do not

- Do not add copyrighted music, MIDI files, or SoundFonts to the repo.
- Do not add accounts, databases, cloud services, or real-time streaming.
- Do not change `Config` defaults to fix a single recording.
- Do not refactor files unrelated to the current task.
