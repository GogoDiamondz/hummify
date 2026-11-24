"""Convert note sequences to downloadable MIDI bytes."""

import io

import pretty_midi

from hummify.models import Note


def notes_to_midi(notes: list[Note], tempo_bpm: float) -> bytes:
    """Serialize beat-timed notes as a single-instrument MIDI file."""
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo_bpm)
    instrument = pretty_midi.Instrument(program=0)
    for note in notes:
        start = note.start_beat * 60.0 / tempo_bpm
        end = (note.start_beat + note.duration_beats) * 60.0 / tempo_bpm
        instrument.notes.append(pretty_midi.Note(velocity=90, pitch=note.midi_pitch, start=start, end=end))
    midi.instruments.append(instrument)
    buffer = io.BytesIO()
    midi.write(buffer)
    return buffer.getvalue()
