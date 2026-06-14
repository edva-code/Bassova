"""Accuracy metrics built on mir_eval, comparing detected notes to ground truth."""

import numpy as np
import mir_eval


def _to_hz(midi_values):
    return 440.0 * (2.0 ** ((np.asarray(midi_values, dtype=float) - 69) / 12))


def _intervals_and_pitches(notes):
    if not notes:
        return np.zeros((0, 2)), np.zeros(0)
    intervals = np.array([[n["start_time"], n["end_time"]] for n in notes], dtype=float)
    pitches = _to_hz([n["pitch_midi"] for n in notes])
    return intervals, pitches


def evaluate(ref_notes, est_notes, onset_tolerance=0.05):
    """Compare estimated notes to reference notes.

    Note F-measure matches a detected note to a reference when their onsets fall
    within onset_tolerance and their pitches agree (within mir_eval's default of
    a quarter tone, so octave errors correctly count as misses). Offsets are
    ignored because detected note ends are noisy. Onset F-measure scores timing
    alone, regardless of pitch.
    """
    ref_intervals, ref_pitches = _intervals_and_pitches(ref_notes)
    est_intervals, est_pitches = _intervals_and_pitches(est_notes)

    note_p, note_r, note_f, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref_intervals,
        ref_pitches,
        est_intervals,
        est_pitches,
        onset_tolerance=onset_tolerance,
        offset_ratio=None,
    )

    onset_f, _, _ = mir_eval.onset.f_measure(
        ref_intervals[:, 0] if len(ref_intervals) else np.zeros(0),
        est_intervals[:, 0] if len(est_intervals) else np.zeros(0),
        window=onset_tolerance,
    )

    return {
        "note_f": note_f,
        "note_precision": note_p,
        "note_recall": note_r,
        "onset_f": onset_f,
        "ref_count": len(ref_notes),
        "est_count": len(est_notes),
    }
