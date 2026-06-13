"""Milestone 1: load an audio file, run pitch detection, print the notes.

Usage:
    python scripts/test_pitch_detection.py path/to/your_recording.wav
"""

import sys
from pathlib import Path

# allow running this script directly from the scripts/ folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

from engine.pitch_detection import detect_notes


# rough MIDI -> note name mapping, useful for sanity-checking results
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_name(midi_number):
    name = NOTE_NAMES[midi_number % 12]
    octave = (midi_number // 12) - 1
    return f"{name}{octave}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_pitch_detection.py <path_to_audio_file>")
        sys.exit(1)

    audio_path = sys.argv[1]
    print(f"Analyzing: {audio_path}\n")

    notes = detect_notes(audio_path)

    print(f"Detected {len(notes)} notes:\n")
    for note in notes:
        duration = note["end_time"] - note["start_time"]
        name = midi_to_name(note["pitch_midi"])
        print(
            f"  {note['start_time']:6.2f}s -> {note['end_time']:6.2f}s "
            f"(dur {duration:5.2f}s)  {name:>4} (MIDI {note['pitch_midi']:3d})  "
            f"amp {note['amplitude']:.2f}"
        )


if __name__ == "__main__":
    main()
