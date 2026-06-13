STRING_NAMES = ["E", "A", "D", "G"]


def render_tab(mapped_notes, bpm=120, subdivisions=16):
    if not mapped_notes:
        return ""

    steps_per_second = (bpm / 60) * (subdivisions / 4)
    last_time = max(n["start_time"] for n in mapped_notes)
    total_steps = int(last_time * steps_per_second) + subdivisions

    grid = [[""] * total_steps for _ in range(4)]

    for note in mapped_notes:
        if note["string"] is None:
            continue
        step = int(round(note["start_time"] * steps_per_second))
        if step < total_steps:
            grid[note["string"]][step] = str(note["fret"])

    lines = []
    for string_index in reversed(range(4)):
        row = []
        for cell in grid[string_index]:
            if cell:
                row.append(cell.ljust(2, "-"))
            else:
                row.append("--")
        lines.append(f"{STRING_NAMES[string_index]} |{''.join(row)}|")

    return "\n".join(lines)
