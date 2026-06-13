TUNING_MIDI = [28, 33, 38, 43]  # E1, A1, D2, G2
MAX_FRET = 20


def map_to_fretboard(notes):
    result = []
    prev_fret = 0

    for note in notes:
        midi = note["pitch_midi"]
        options = []

        for string_index, open_midi in enumerate(TUNING_MIDI):
            fret = midi - open_midi
            if 0 <= fret <= MAX_FRET:
                options.append((string_index, fret))

        if not options:
            mapped = {**note, "string": None, "fret": None}
        else:
            string_index, fret = min(options, key=lambda o: abs(o[1] - prev_fret))
            prev_fret = fret
            mapped = {**note, "string": string_index, "fret": fret}

        result.append(mapped)

    return result
