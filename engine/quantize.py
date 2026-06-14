"""Snap detected note onsets to a rhythmic grid for clean tab rendering."""

import numpy as np


def grid_step_seconds(bpm, subdivisions=16):
    """Duration of one grid step in seconds. subdivisions=16 gives sixteenth notes."""
    return (60.0 / bpm) * (4.0 / subdivisions)


def estimate_offset(start_times, step):
    """Estimate the grid phase offset (in seconds) that best fits all onsets.

    A take rarely begins exactly on the beat, so a fixed grid anchored at time 0
    would misalign every note. We treat each onset's position within a step as an
    angle and take the circular mean, which gives the offset that minimises the
    overall snapping error. Result is in the range [-step/2, step/2].
    """
    if len(start_times) == 0:
        return 0.0
    phases = (np.asarray(start_times, dtype=float) % step) / step  # 0..1 within a step
    angles = 2 * np.pi * phases
    mean_angle = np.angle(np.mean(np.exp(1j * angles)))            # -pi..pi
    return (mean_angle / (2 * np.pi)) * step


def fit_bpm(notes, bpm_hint, subdivisions=16, search=0.10, candidates=41, anchor=0.05):
    """Refine a BPM hint by finding the nearby tempo whose grid best fits the onsets.

    Global tempo detection from bass alone is unreliable, but once the user (or
    auto-detection, or tap tempo) provides a roughly correct BPM, the detected
    note onsets pin down the exact tempo. We search a narrow band around the hint
    and pick the tempo with the smallest average snapping error, plus a light
    anchor term so we stay close to the hint when the fit is ambiguous.

    The narrow band matters: a grid twice as fine fits any onset equally well, so
    searching far would drift toward meaningless half/double tempos. Staying within
    a few percent only corrects small errors and the drift they cause over a long
    take, which is exactly what makes the rendered rhythm line up.
    """
    starts = [n["start_time"] for n in notes]
    if len(starts) < 4:
        return float(bpm_hint)

    starts = np.asarray(starts, dtype=float)
    best_bpm, best_cost = float(bpm_hint), float("inf")
    for bpm in np.linspace(bpm_hint * (1 - search), bpm_hint * (1 + search), candidates):
        step = grid_step_seconds(bpm, subdivisions)
        offset = estimate_offset(starts, step)
        frac = (starts - offset) / step
        snap = float(np.mean(np.abs(frac - np.round(frac))))
        cost = snap + anchor * abs(bpm - bpm_hint) / bpm_hint
        if cost < best_cost:
            best_cost, best_bpm = cost, float(bpm)

    return best_bpm


def quantize_notes(notes, bpm, subdivisions=16, refine=True):
    """Return notes with an added integer 'step' (grid index counted from time 0).

    Onsets are snapped to the nearest grid line after correcting for the overall
    phase offset. When several notes land on the same step, the monophonic bass
    keeps the one whose true onset sits closest to that grid line. With refine on,
    the BPM is first locked to the nearby tempo that best fits the onsets.
    """
    if not notes:
        return []

    if refine:
        bpm = fit_bpm(notes, bpm, subdivisions)

    step = grid_step_seconds(bpm, subdivisions)
    offset = estimate_offset([n["start_time"] for n in notes], step)

    best_per_step = {}
    for note in notes:
        position = (note["start_time"] - offset) / step
        index = max(0, int(round(position)))
        distance = abs(position - index)
        current = best_per_step.get(index)
        if current is None or distance < current[1]:
            best_per_step[index] = ({**note, "step": index}, distance)

    ordered = [best_per_step[i][0] for i in sorted(best_per_step)]
    _add_durations(ordered, offset, step)
    return ordered


def _add_durations(ordered, offset, step):
    """Fill in how long each note sounds and the rest after it, in grid steps.

    For a monophonic bass the rhythmic slot of a note runs from its onset to the
    next onset. We treat that whole slot as held unless the detected note end is
    clearly short, in which case the leftover becomes a rest. Detected note ends
    are noisy, so a small gap is ignored and only a clear early stop creates a rest.
    """
    for i, note in enumerate(ordered):
        onset_step = note["step"]
        end_step = int(round((note.get("end_time", note["start_time"]) - offset) / step))
        detected = max(1, end_step - onset_step)

        if i + 1 < len(ordered):
            slot = max(1, ordered[i + 1]["step"] - onset_step)
            if detected <= slot * 0.6:
                sustain, rest = detected, slot - detected
            else:
                sustain, rest = slot, 0
        else:
            sustain, rest = detected, 0

        note["sustain_steps"] = max(1, sustain)
        note["rest_steps"] = max(0, rest)
