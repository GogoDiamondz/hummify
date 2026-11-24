"""Score note transcriptions against annotated reference notes."""

from collections.abc import Sequence

import mir_eval
import numpy as np

from hummify.models import Note


def score_notes(reference: Sequence[Note], estimate: Sequence[Note], tempo_bpm: float) -> dict[str, float]:
    """Return onset-and-offset and onset-only precision, recall, and F1."""
    if tempo_bpm <= 0:
        raise ValueError("tempo_bpm must be positive")
    beat_seconds = 60.0 / tempo_bpm

    def arrays(notes: Sequence[Note]) -> tuple[np.ndarray, np.ndarray]:
        intervals = np.asarray([
            [note.start_beat * beat_seconds, (note.start_beat + note.duration_beats) * beat_seconds]
            for note in notes
        ], dtype=float).reshape((-1, 2))
        pitches = np.asarray([float(note.midi_pitch) for note in notes], dtype=float)
        return intervals, pitches

    ref_intervals, ref_pitches = arrays(reference)
    est_intervals, est_pitches = arrays(estimate)
    p, r, f, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref_intervals, ref_pitches, est_intervals, est_pitches,
        onset_tolerance=0.05, pitch_tolerance=0.5)
    po, ro, fo, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref_intervals, ref_pitches, est_intervals, est_pitches,
        onset_tolerance=0.05, pitch_tolerance=0.5, offset_ratio=None)
    return {"precision": float(p), "recall": float(r), "f1": float(f),
            "onset_only_precision": float(po), "onset_only_recall": float(ro), "onset_only_f1": float(fo)}


def main() -> None:
    """Evaluate annotated JSON recordings in a directory."""
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Score manually transcribed notes against JSON ground truth.")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    files = sorted(args.directory.glob("*.json"))
    if not files:
        parser.error(f"No ground-truth JSON files found in {args.directory}")
    scores = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        references = [Note(item["start_beat"], item["duration_beats"], item["midi_pitch"]) for item in data["reference_notes"]]
        estimates = [Note(item["start_beat"], item["duration_beats"], item["midi_pitch"]) for item in data["estimated_notes"]]
        scores.append(score_notes(references, estimates, data["tempo_bpm"]))
    keys = scores[0]
    print(f"Recordings: {len(files)}")
    for key in keys:
        print(f"{key}: {np.mean([score[key] for score in scores]):.3f}")


if __name__ == "__main__":
    main()
