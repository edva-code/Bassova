import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from engine.pitch_detection import detect_notes
from engine.fretboard_mapping import map_to_fretboard
from engine.tab_renderer import render_tab


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_tab.py <audio_file> [bpm]")
        sys.exit(1)

    audio_path = sys.argv[1]
    bpm = int(sys.argv[2]) if len(sys.argv) > 2 else 120

    notes = detect_notes(audio_path)
    mapped = map_to_fretboard(notes)
    tab = render_tab(mapped, bpm=bpm)

    print(tab)


if __name__ == "__main__":
    main()
