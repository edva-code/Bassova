import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from engine.pitch_detection import detect_notes
from engine.fretboard_mapping import map_to_fretboard

STRING_NAMES = ["E", "A", "D", "G"]
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{(midi // 12) - 1}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_fretboard.py <audio_file>")
        sys.exit(1)

    notes = detect_notes(sys.argv[1])
    mapped = map_to_fretboard(notes)

    print(f"{'Time':>7}  {'Note':>4}  {'String':>6}  {'Fret':>4}")
    print("-" * 30)
    for n in mapped:
        name = midi_to_name(n["pitch_midi"])
        string = STRING_NAMES[n["string"]] if n["string"] is not None else "?"
        fret = n["fret"] if n["fret"] is not None else "?"
        print(f"{n['start_time']:7.2f}  {name:>4}  {string:>6}  {fret:>4}")


if __name__ == "__main__":
    main()
