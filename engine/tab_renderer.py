from engine.quantize import quantize_notes

STRING_NAMES = ["E", "A", "D", "G"]


def render_tab(mapped_notes, bpm=120, subdivisions=16, bars_per_line=4):
    playable = [n for n in mapped_notes if n.get("string") is not None]
    if not playable:
        return ""

    quantized = quantize_notes(playable, bpm, subdivisions)

    # round the length up to a whole number of bars so every line is even
    last_step = max(n["step"] for n in quantized)
    total_steps = ((last_step // subdivisions) + 1) * subdivisions

    grid = [[""] * total_steps for _ in range(4)]
    for note in quantized:
        if note["step"] < total_steps:
            grid[note["string"]][note["step"]] = str(note["fret"])

    steps_per_line = subdivisions * bars_per_line
    sections = []

    for start in range(0, total_steps, steps_per_line):
        end = min(start + steps_per_line, total_steps)
        lines = []
        for string_index in reversed(range(4)):
            row = []
            for i, step in enumerate(range(start, end)):
                cell = grid[string_index][step]
                if i > 0 and i % subdivisions == 0:
                    row.append("|")
                if cell:
                    row.append(cell.ljust(2, "-"))
                else:
                    row.append("--")
            lines.append(f"{STRING_NAMES[string_index]} |{''.join(row)}|")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
