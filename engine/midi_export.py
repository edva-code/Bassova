import tempfile
import pretty_midi


def export_to_temp_midi(mapped_notes, tempo_bpm=120):
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo_bpm)
    bass = pretty_midi.Instrument(program=33)  # Electric Bass (finger)

    for note in mapped_notes:
        if note["string"] is None:
            continue
        velocity = min(127, max(40, int(note["amplitude"] * 100) + 27))
        midi_note = pretty_midi.Note(
            velocity=velocity,
            pitch=note["pitch_midi"],
            start=note["start_time"],
            end=note["end_time"],
        )
        bass.notes.append(midi_note)

    midi.instruments.append(bass)
    tmp = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
    midi.write(tmp.name)
    tmp.close()
    return tmp.name
