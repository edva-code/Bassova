from engine.quantize import quantize_notes

STRING_NAMES = ["E", "A", "D", "G"]

EMPTY_CELL = "--"      # nothing sounding (silence or a rest)
SUSTAIN_CELL = "=="    # a note from an earlier step is still ringing


def render_tab(mapped_notes, bpm=120, subdivisions=16, bars_per_line=4):
    playable = [n for n in mapped_notes if n.get("string") is not None]
    if not playable:
        return ""

    quantized = quantize_notes(playable, bpm, subdivisions)

    # the grid must reach the end of the last note that is still ringing
    last_col = max(n["step"] + n["sustain_steps"] - 1 for n in quantized)
    total_steps = ((last_col // subdivisions) + 1) * subdivisions

    grid = [[EMPTY_CELL] * total_steps for _ in range(4)]
    for note in quantized:
        string = note["string"]
        onset = note["step"]
        held = note["sustain_steps"] > 1
        grid[string][onset] = str(note["fret"]).ljust(2, "=" if held else "-")
        for offset in range(1, note["sustain_steps"]):
            col = onset + offset
            if col < total_steps:
                grid[string][col] = SUSTAIN_CELL

    steps_per_line = subdivisions * bars_per_line
    sections = []

    for start in range(0, total_steps, steps_per_line):
        end = min(start + steps_per_line, total_steps)
        lines = []
        for string_index in reversed(range(4)):
            row = []
            for i, step in enumerate(range(start, end)):
                if i > 0 and i % subdivisions == 0:
                    row.append("|")
                row.append(grid[string_index][step])
            lines.append(f"{STRING_NAMES[string_index]} |{''.join(row)}|")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
