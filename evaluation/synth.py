"""Generate synthetic bass recordings with known ground-truth notes.

Labelled real bass data is scarce, so for a reproducible accuracy benchmark we
render known note sequences to audio with a simple harmonic synth and run that
through the pipeline. The notes we rendered are the ground truth.

This measures the detection and post-processing, not real-instrument timbre, so
read the numbers as a relative score for tuning and catching regressions, not as
an absolute promise about real recordings. Drop real audio plus a ground-truth
MIDI into a case later to measure that too.
"""

import numpy as np
import soundfile as sf

SAMPLE_RATE = 22050
DECAY_RATE = 2.5    # exponential decay per second, like a plucked string
ATTACK_SECONDS = 0.005  # short fade in so note onsets do not click


def _harmonic_wave(phase):
    """A richer tone than a bare sine, so the detector has overtones to work with."""
    return (
        np.sin(phase)
        + 0.5 * np.sin(2 * phase)
        + 0.33 * np.sin(3 * phase)
        + 0.2 * np.sin(4 * phase)
    )


def _midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def notes_from_spec(spec, bpm):
    """Convert (midi, start_beat, length_beats) tuples into note dicts in seconds."""
    seconds_per_beat = 60.0 / bpm
    notes = []
    for midi, start_beat, length_beats in spec:
        start = start_beat * seconds_per_beat
        end = (start_beat + length_beats) * seconds_per_beat
        notes.append(
            {
                "start_time": round(start, 4),
                "end_time": round(end, 4),
                "pitch_midi": int(midi),
                "amplitude": 1.0,
            }
        )
    return notes


def render_case(spec, bpm, path):
    """Render a note spec to a WAV file and return the ground-truth note dicts.

    Each note is a harmonic tone with a plucked-string decay envelope, mixed into
    one buffer. The decay matters: a constant-amplitude sustain made the detector
    invent extra notes mid-tone, which is not how a real bass behaves.
    """
    notes = notes_from_spec(spec, bpm)

    total_seconds = max(n["end_time"] for n in notes) + 0.5
    audio = np.zeros(int(total_seconds * SAMPLE_RATE) + 1)
    attack = max(1, int(ATTACK_SECONDS * SAMPLE_RATE))

    for note in notes:
        start = int(note["start_time"] * SAMPLE_RATE)
        length = int((note["end_time"] - note["start_time"]) * SAMPLE_RATE)
        if length <= 0:
            continue
        t = np.arange(length) / SAMPLE_RATE
        envelope = np.exp(-DECAY_RATE * t)
        envelope[:attack] *= np.linspace(0.0, 1.0, attack)
        segment = _harmonic_wave(2 * np.pi * _midi_to_hz(note["pitch_midi"]) * t) * envelope
        audio[start:start + length] += segment

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = 0.9 * audio / peak
    sf.write(path, audio.astype(np.float32), SAMPLE_RATE)

    return notes


# Benchmark cases: (name, bpm, spec) where spec is a list of (midi, start_beat, length_beats).
# Pitches stay within a standard 4-string bass range (E1 = 28 up to the G string).
CASES = [
    (
        "quarter_walk",
        100,
        [
            (28, 0, 1), (33, 1, 1), (35, 2, 1), (36, 3, 1),
            (38, 4, 1), (36, 5, 1), (35, 6, 1), (33, 7, 1),
        ],
    ),
    (
        "eighth_groove",
        120,
        [
            (28, 0, 0.5), (28, 0.5, 0.5), (35, 1, 0.5), (28, 1.5, 0.5),
            (33, 2, 0.5), (33, 2.5, 0.5), (40, 3, 0.5), (33, 3.5, 0.5),
        ],
    ),
    (
        "with_rests",
        90,
        [
            (31, 0, 1), (31, 2, 1), (38, 3, 0.5),
            (36, 4, 1), (33, 6, 2),
        ],
    ),
    (
        "range_jumps",
        110,
        [
            (28, 0, 1), (43, 1, 1), (31, 2, 1), (45, 3, 1),
            (33, 4, 1), (40, 5, 1), (29, 6, 1), (41, 7, 1),
        ],
    ),
]
