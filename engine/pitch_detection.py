"""Wrapper around Basic Pitch for note (pitch + onset) detection, tuned for bass."""

from basic_pitch.inference import predict

# A 4-string bass spans roughly E1 (41 Hz) up to the high frets on the G string.
# 5-string basses add a low B (31 Hz). Constraining Basic Pitch to this band
# removes most high-frequency false positives and octave-up ghost notes at the
# source, before any post-processing runs.
MIN_FREQUENCY = 30.0    # Hz, just below low B on a 5-string
MAX_FREQUENCY = 500.0   # Hz, above the highest practical fretted bass note

# Basic Pitch detection thresholds. Bass notes are sustained and well defined,
# so we can demand a longer minimum note length to reject transient blips.
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
MINIMUM_NOTE_LENGTH_MS = 90.0

ONSET_TOLERANCE = 0.05  # seconds: notes starting within this window are simultaneous
MIN_AMPLITUDE = 0.10    # drop very weak notes that are usually noise or string bleed
STRONG_RATIO = 0.4      # in a cluster, only notes this loud relative to the peak count


def detect_notes(audio_path):
    """Run pitch and onset detection on an audio file.

    Returns:
        A list of dicts, one per detected note, each with:
            start_time: note start in seconds
            end_time: note end in seconds
            pitch_midi: MIDI note number (e.g. 40 = E1)
            amplitude: rough confidence/velocity value, 0 to 1
    """
    _, _, note_events = predict(
        audio_path,
        onset_threshold=ONSET_THRESHOLD,
        frame_threshold=FRAME_THRESHOLD,
        minimum_note_length=MINIMUM_NOTE_LENGTH_MS,
        minimum_frequency=MIN_FREQUENCY,
        maximum_frequency=MAX_FREQUENCY,
        melodia_trick=True,
    )

    notes = []
    for event in note_events:
        start_time, end_time, pitch_midi, amplitude = event[:4]
        notes.append(
            {
                "start_time": round(float(start_time), 3),
                "end_time": round(float(end_time), 3),
                "pitch_midi": int(pitch_midi),
                "amplitude": round(float(amplitude), 3),
            }
        )

    notes.sort(key=lambda n: n["start_time"])
    notes = [n for n in notes if n["amplitude"] >= MIN_AMPLITUDE]
    notes = _collapse_simultaneous(notes)
    return notes


def _collapse_simultaneous(notes):
    """Bass is monophonic: notes that start almost together are harmonics or
    octave ghosts of a single real note. For each near-simultaneous cluster,
    keep the lowest pitch among the reasonably strong detections.

    This subsumes the older octave-doubling filter (an octave ghost is just one
    kind of higher partial firing at the same instant) and also catches fifths
    and other harmonics that Basic Pitch sometimes reports for bass.
    """
    if not notes:
        return notes

    result = []
    i = 0
    n = len(notes)
    while i < n:
        j = i + 1
        while j < n and notes[j]["start_time"] - notes[i]["start_time"] <= ONSET_TOLERANCE:
            j += 1
        cluster = notes[i:j]
        peak = max(c["amplitude"] for c in cluster)
        strong = [c for c in cluster if c["amplitude"] >= STRONG_RATIO * peak]
        result.append(min(strong, key=lambda c: c["pitch_midi"]))
        i = j

    return result
