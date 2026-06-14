TUNING_MIDI = [28, 33, 38, 43]  # E1, A1, D2, G2
MAX_FRET = 20

OPEN_STRING_BONUS = 0.5  # open strings are easy to play, so prefer them slightly
LOW_FRET_WEIGHT = 0.1    # mild preference for lower frets when positions tie


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
            result.append({**note, "string": None, "fret": None})
            continue

        string_index, fret = min(options, key=lambda o: _position_cost(o[1], prev_fret))
        prev_fret = fret
        result.append({**note, "string": string_index, "fret": fret})

    return result


def _position_cost(fret, prev_fret):
    """Lower cost means a more natural choice for a human player.

    The dominant term keeps the hand near its previous position. A small low-fret
    weight breaks ties toward the easier lower frets, and open strings get a
    slight bonus since they need no fretting hand at all.
    """
    cost = abs(fret - prev_fret) + LOW_FRET_WEIGHT * fret
    if fret == 0:
        cost -= OPEN_STRING_BONUS
    return cost
