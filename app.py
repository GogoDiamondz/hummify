"""Streamlit UI for Hummify's transcription pipeline."""

import librosa
import streamlit as st

from hummify.audio_io import load_audio
from hummify.config import Config
from hummify.export import notes_to_midi
from hummify.pitch import track_pitch
from hummify.playback import synthesize
from hummify.segment import segment_pitch_frames

st.set_page_config(page_title="Hummify", page_icon="🎵")
st.title("Hummify")
st.write("Record a melody or upload audio to see its detected notes.")
recording = st.audio_input("Record a hum")
upload = st.file_uploader("Or upload WAV / MP3", type=["wav", "mp3"])
source = recording if recording is not None else upload

if source is not None:
    config = Config()
    tempo = st.number_input("Tempo (BPM)", min_value=40, max_value=240, value=int(config.default_tempo_bpm))
    audio, sample_rate = load_audio(source.getvalue(), config.sample_rate)
    times, midi, voiced = track_pitch(audio, sample_rate, config)
    notes = segment_pitch_frames(times, midi, voiced, tempo, config)
    st.audio(source)
    if notes:
        st.subheader("Detected notes")
        st.dataframe([{"Start (beat)": round(n.start_beat, 2), "Duration (beats)": round(n.duration_beats, 2), "MIDI pitch": n.midi_pitch, "Note": librosa.midi_to_note(n.midi_pitch)} for n in notes], hide_index=True)
        st.audio(synthesize(notes, tempo, config), sample_rate=config.synth_sample_rate)
        st.download_button("Download MIDI", notes_to_midi(notes, tempo), file_name="hummify.mid", mime="audio/midi")
    else:
        st.info("No voiced notes were detected. Try a clearer recording.")
