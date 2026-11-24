# AGENTS.md

## Project

Hummify is a class project. The user hums a melody (recorded in the browser or uploaded as WAV/MP3). The app transcribes it into notes with pitch and duration, plays the notes back, and exports MIDI. Later phases add sheet music (MusicXML) and note editing.

The design document is the source of truth for scope and decisions. If a task conflicts with it, ask before changing direction.

**Current phase:** 3 (evaluation script and baseline setup). Update this line as phases finish.

| Phase | Scope |
|---|---|
| 1 | Record or upload, pYIN pitch tracking, semitone snapping, notes listed |
| 2 | Note segmentation, metronome-based quantization, MIDI export, playback |
| 3 | Evaluation script, test recordings, baseline numbers |
| 4 | Key snapping, Basic Pitch comparison, threshold tuning |
| 5 | Sheet music display (MusicXML) and note editing |
| 6 | Report and demo |

Do not build features from a later phase unless asked.

## Stack

- Python 3.11+
- UI: Streamlit
- Audio and pitch: `librosa` (pYIN), `numpy`, `soundfile`
- Music data: `pretty_midi` (MIDI), `music21` (key detection, MusicXML)
- Evaluation: `mir_eval`
- Tests: `pytest`

Prefer these libraries over adding new dependencies. If a new dependency is really needed, say why and add it to `requirements.txt`.

## Layout

```
app.py                  Streamlit entry point (UI only)
hum2notes/
  config.py             All tunable thresholds (single Config dataclass)
  models.py             Note dataclass: start_beat, duration_beats, midi_pitch
  audio_io.py           Load, record, resample audio
  pitch.py              Audio -> per-frame frequency + voiced flag
  segment.py            Frames -> raw notes
  quantize.py           Snap pitch (semitone/scale) and timing (beat grid)
  export.py             Notes -> MIDI / MusicXML
  playback.py           Notes -> audio array (numpy synth by default)
  evaluate.py           Score output against ground truth with mir_eval
tests/                  One test file per module
data/test_recordings/   Hummed test clips + ground-truth notes
```

## Architecture rules

1. Each pipeline stage is a pure function: arrays or dataclasses in, arrays or dataclasses out. No file access, global state, or Streamlit calls inside `pitch`, `segment`, `quantize`, `export`, `playback`, or `evaluate`.
2. All tunable numbers (semitone threshold, minimum note length, median-filter size, grid resolution, and similar) live in `config.py`. Never hard-code them in algorithm files.
3. `app.py` only wires UI to the pipeline. No algorithm logic there.
4. Pipeline order: `audio_io` -> `pitch` -> `segment` -> `quantize` -> notes -> (`export` | `playback` | UI).
5. Internal pitch representation is fractional MIDI note numbers. Convert from Hz once, in `pitch.py`.
6. Internal time representation after quantization is beats, not seconds.

## Algorithm notes

- Pitch tracking: pYIN, then a median filter to remove octave jumps and smooth vibrato. Drop unvoiced frames.
- Segmentation: start a new note when pitch moves about 0.7 to 1 semitone from the running note median and stays there for a minimum number of frames, or when the signal goes unvoiced or energy dips sharply. Merge notes shorter than about 80 ms into neighbors.
- Quantization: use the metronome click for tempo and downbeat. Fall back to a user-entered tempo. Default grid is sixteenth notes.
- Key snapping is optional and off by default until phase 4.
- Playback default is a numpy sine or triangle synth. FluidSynth is optional; never make it a hard requirement.

## Commands

```
pip install -r requirements.txt
streamlit run app.py
pytest
python -m hum2notes.evaluate data/test_recordings
```

Run `pytest` and the evaluation script after any change to `pitch`, `segment`, or `quantize`, and report whether the F1 score went up or down.

## Testing and evaluation

- Use standard `pytest` or Python's built-in `unittest`; do not add or rely on BYU-specific tools or plugins.
- Add or update a test in `tests/` for every function you change.
- Use synthetic audio (generated sine tones with known pitches and durations) for unit tests, so tests do not depend on recordings.
- The evaluation script uses `mir_eval.transcription` with a 50 ms onset tolerance and 50 cent pitch tolerance. Report precision, recall, and F1.
- Never overwrite files in `data/test_recordings/`.

## Code style

- Type hints on all public functions. Docstring on each module and public function, one or two lines.
- Small functions. Prefer clear names over comments.
- Format with `black` and lint with `ruff` if configured.
- Do not leave debug prints or commented-out code.

## Do not

- Do not commit copyrighted music, MIDI files, or SoundFonts. Link to downloads instead.
- Do not add accounts, databases, cloud services, or real-time streaming transcription.
- Do not change `config.py` default values to fix one recording. Make a change that helps the whole test set, or add a config option.
- Do not refactor unrelated files while working on a task.

## Working with the maintainer

- For a change that touches more than one module, outline the plan first, then implement.
- When a change affects accuracy, include before and after evaluation numbers in your summary.
- If a requirement is ambiguous, ask one short question instead of guessing.
