"""Wrapper around Basic Pitch for note (pitch + onset) detection."""

from basic_pitch.inference import predict

ONSET_TOLERANCE = 0.05  # seconds: notes starting within this window are considered simultaneous


def detect_notes(audio_path):
    """Run pitch and onset detection on an audio file.

    Returns:
        A list of dicts, one per detected note, each with:
            start_time: note start in seconds
            end_time: note end in seconds
            pitch_midi: MIDI note number (e.g. 40 = E1)
            amplitude: rough confidence/velocity value, 0 to 1
    """
    _, _, note_events = predict(audio_path)

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
    return _filter_octave_doublings(notes)


def _filter_octave_doublings(notes):
    """Remove octave ghost notes produced by harmonic content in bass recordings.

    Basic Pitch often detects both the fundamental and an octave above simultaneously.
    When two notes start within ONSET_TOLERANCE of each other and differ by exactly
    12 MIDI semitones, only the lower one is kept.
    """
    keep = [True] * len(notes)

    for i, note in enumerate(notes):
        if not keep[i]:
            continue
        for j in range(i + 1, len(notes)):
            other = notes[j]
            if other["start_time"] - note["start_time"] > ONSET_TOLERANCE:
                break
            if abs(other["pitch_midi"] - note["pitch_midi"]) == 12:
                # drop whichever is higher
                if other["pitch_midi"] > note["pitch_midi"]:
                    keep[j] = False
                else:
                    keep[i] = False
                    break

    return [n for n, k in zip(notes, keep) if k]
