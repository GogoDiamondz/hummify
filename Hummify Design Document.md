# Hummify: Design Document

*Class project, draft v0.2. The author's answers are in Section 12.*

## 1. Overview

Hummify is a songwriting aid. The user hums a melody into the microphone (or uploads a recording), and the app transcribes it into notes with pitch and duration, shows them in a piano roll, plays them back, and exports them as MIDI.

**Goals**

- Turn a monophonic hum into a clean, editable note sequence.
- Let the user hear the transcription and compare it to their hum.
- Export to MIDI so the result can go into a DAW or notation tool.
- Produce measurable accuracy numbers for the class report.

**Non-goals**

- Song identification or similarity search (the earlier idea).
- Polyphonic transcription (chords, multiple voices).
- Mobile apps, user accounts, or cloud storage.
- Real-time live transcription while humming (stretch goal only).

## 2. Users and Use Cases

Primary user: a hobbyist songwriter with no music-notation skills who wants to capture a melody idea quickly.

1. Record a hum with a metronome click, see notes appear, play them back.
2. Fix a few wrong notes in the piano roll.
3. Export the result as a MIDI file.

## 3. Requirements

**Must have**

- Record from mic or upload a WAV/MP3.
- Pitch tracking with voiced/unvoiced detection.
- Note segmentation and semitone snapping.
- Tempo-aware rhythm quantization.
- Piano-roll display and audio playback.
- MIDI export.

**Should have**

- Key detection with optional scale snapping.
- Note editing (move, delete, change length), wanted by the author and built after the core pipeline works.
- Evaluation script with `mir_eval` metrics.
- Comparison against Basic Pitch as a baseline.

**Could have**

- Sheet music display and MusicXML export, wanted by the author and built after the core pipeline works.
- Live transcription during recording.
- Multiple takes per project.

## 4. Proposed Architecture

*Assumption: Python with a Streamlit or Gradio front end. See Open Questions.*

```
Mic / file  ->  Preprocess  ->  Pitch tracker  ->  Segmenter  ->  Quantizer  ->  Notes
                                                                                   |
                                                       Piano roll  <-  Editor  <---+
                                                       Playback    <---------------+
                                                       MIDI export <---------------+
```

| Module | Responsibility | Library |
| --- | --- | --- |
| `audio_io` | Record, load, resample to a fixed sample rate | `librosa`, `soundfile` |
| `pitch` | Frame-wise f0 plus voiced flag | `librosa.pyin` (CREPE as an alternative) |
| `segment` | Group frames into notes | `numpy`, custom logic |
| `quantize` | Snap pitch to semitone/scale and timing to grid | `numpy`, `music21` (key detection) |
| `export` | Write MIDI or MusicXML | `pretty_midi`, `music21` |
| `playback` | Render notes to audio | numpy synth, or FluidSynth plus a SoundFont |
| `ui` | Record, display, edit, download | Streamlit or Gradio |
| `eval` | Score output against ground truth | `mir_eval` |

Keep each stage a pure function (arrays in, arrays out) so stages can be tested and swapped independently.

## 5. Algorithm Design

### 5.1 Pitch tracking

Run pYIN over the recording to get a frequency and a voiced/unvoiced flag per frame. Apply a median filter to remove octave jumps and smooth vibrato. Discard unvoiced frames.

### 5.2 Note segmentation (the hard part)

Convert frequency to fractional MIDI numbers. Start a new note when either:

- the pitch moves more than about 0.7 to 1 semitone from the running note median and stays there for a minimum number of frames, or
- the signal goes unvoiced, or the energy dips sharply (a new syllable such as "da").

Merge notes shorter than a minimum duration (around 80 ms) into their neighbors. All thresholds live in one config object so they can be tuned and evaluated.

### 5.3 Pitch snapping

Round each note to the nearest semitone. Optionally estimate the key (Krumhansl-Schmuckler on the note histogram) and snap to that scale. Correct for slow drift by estimating a running tuning offset.

### 5.4 Rhythm quantization

Use a metronome click during recording so tempo is known and the first beat is anchored. Snap onsets and durations to a grid (default: sixteenth notes). If there is no click, fall back to a user-entered tempo.

### 5.5 Output

A list of `(start_beat, duration_beats, midi_pitch)` tuples, which feeds the piano roll, playback, and MIDI export.

## 6. User Interface

One page with four areas:

1. **Controls:** tempo, metronome on/off, key snap on/off, record and upload buttons.
2. **Waveform / pitch curve:** the raw f0 trace, so the user can see what the tracker heard.
3. **Piano roll:** transcribed notes, editable in phase 5.
4. **Output bar:** play transcription, play original hum, download MIDI.

Showing the raw pitch curve behind the piano roll is useful for debugging segmentation and makes a good figure for the report.

**Sheet music:** render the MusicXML export with OpenSheetMusicDisplay, a free JavaScript library, embedded in Streamlit with `st.components.v1.html`. **Editing:** Streamlit has no built-in piano roll, so start with an editable table of notes (start, duration, pitch) using `st.data_editor`, re-render the sheet music and playback on each change, and build a drag-and-drop piano roll only if time remains.

## 7. Playback

MIDI contains no sound, so a synth is needed. Start with a numpy-generated sine or triangle wave (about 20 lines, no dependencies). Upgrade to FluidSynth with a free SoundFont such as GeneralUser GS only if time allows. Link to the SoundFont rather than committing it to the repo.

## 8. Evaluation Plan

**Test set:** 10 to 20 short melodies with known notes (nursery rhymes and simple folk tunes), hummed by the author, ideally with a few from friends. Cover three styles: "da da da", "la la la", and smooth "mmm".

**Metrics** (via `mir_eval.transcription`):

- Note precision, recall, and F1 with 50 ms onset tolerance and 50 cent pitch tolerance.
- The same metrics ignoring offsets.

**Experiments**

| Variant | Question answered |
| --- | --- |
| pYIN vs CREPE | Does the heavier tracker help on hums? |
| With vs without key snapping | How much does scale snapping fix? |
| With vs without metronome | How much does a click improve rhythm? |
| Ours vs Basic Pitch | Does a humming-specific pipeline beat a general one? |
| Syllable type | Where does segmentation break down? |

Save the test recordings and re-run the full evaluation after every change so improvements are measurable.

## 9. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Segmentation is inaccurate on smooth humming | Develop on "da" syllables first, add "mmm" later, tune thresholds against the eval set |
| Octave errors from the pitch tracker | Median filter, octave folding relative to a running median |
| Pitch drift over a phrase | Running tuning offset, key snapping |
| Rhythm is hard without a reference | Metronome click by default |
| FluidSynth install problems | Numpy synth as the default |
| Browser mic permission issues in the UI | Support file upload as a fallback |
| Too little time | Cut scope in the order listed under Milestones |

## 10. Milestones

| Phase | Deliverable | Estimate |
| --- | --- | --- |
| 1 | Record or upload, pYIN, semitone snap, notes listed | 2 to 4 hours |
| 2 | Segmentation, metronome quantization, MIDI export, playback | 1 to 2 days |
| 3 | Evaluation script, test recordings, baseline numbers | 1 day |
| 4 | Key snapping, Basic Pitch comparison, tuning | 1 to 2 days |
| 5 | Sheet music display and note editing | 2 to 3 days (cut first if short on time) |
| 6 | Report and demo | 1 to 2 days |

The phases total roughly 6 to 11 working days, which fits the two-week window with a few days of slack.

## 11. Data, Licensing, and Ethics

- No copyrighted music is needed. All test data is the author's own hums of public-domain tunes.
- If recordings from other people are used, get their consent and keep the files out of the public repo unless they agree.
- SoundFonts and libraries are used under their own licenses and credited in the report.

## 12. Decisions and Open Questions

The author has about two weeks, will use Copilot and Codex, and accepted the defaults for everything else.

| Question | Decision |
| --- | --- |
| Platform | Python with Streamlit |
| Course deliverable | Report plus demo (confirm against the syllabus) |
| Deadline | About two weeks, so phases 1 to 6 fit |
| Vibe coding tools | GitHub Copilot and Codex |
| Humming style | Support both; optimize "da" first |
| Metronome | Click track by default, manual tempo as fallback |
| Output | MIDI first; sheet music (MusicXML) in phase 5 |
| Editing | Phase 5, after the core pipeline works |

## 13. Working with Copilot and Codex

- Add a short context file to the repo: `AGENTS.md` for Codex and `.github/copilot-instructions.md` for Copilot. Each should describe the module layout in Section 4 and the rule that every stage is a pure function.
- Hand each tool one module at a time, with a test, so it never needs the whole project in context.
- Commit the test recordings and the evaluation script early, and run them after every AI-generated change to catch regressions.
- Keep all segmentation thresholds in one config file so tuning prompts touch a single place.
