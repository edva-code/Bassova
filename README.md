# Bassova

Bassova is an app that turns music, recorded and eventually live, into bass guitar tabs and sheet music.

## What it does

Bassova listens to a bass part (either an isolated recording or a full mix) and automatically transcribes it into:

- Tablature (tab): mapped to a standard 4 string bass fretboard
- Sheet music: standard notation with rhythm and key signature

The goal is to make learning, transcribing, or documenting bass lines faster, without doing it note by note by ear.

## Why bass

Automatic music transcription is a hard, well known problem in general, but bass is one of the more tractable starting points. Bass parts are usually monophonic (one note at a time), played in a well defined low frequency range, which makes pitch detection significantly more reliable than for full polyphonic mixes.

## How it works

1. Audio input: load a recorded bass file (wav, mp3, flac)
2. Pitch and onset detection: identify which notes are played and when, using Spotify's Basic Pitch model constrained to the bass frequency range. Octave and harmonic ghost notes are filtered out, very weak detections are dropped, and a second pass reads the model's own salience map to recover clear onsets the first pass missed, which mainly helps fast passages
3. Fretboard mapping: assign each note to a string and fret on a standard 4-string bass (EADG), using a weighted position cost so the hand stays in a natural low position
4. Rhythm quantization: correct the grid phase offset so a take that does not start on the beat still lines up, refine the tempo to best fit the detected onsets, then snap each note to a sixteenth-note grid
5. Tab rendering: lay out the notes on a 4-line ASCII tab grid, broken into bars, showing how long each note is held and the rests between notes
6. Playback: export the result to MIDI and play it back, so you can check by ear whether the tab matches the recording
7. Source separation (planned): isolate bass from a full band recording before transcription
8. Sheet music export (planned): render as standard notation via MusicXML

## Status

Early working prototype. The full pipeline from audio file to ASCII tab is running inside a desktop app:

- Load a bass recording and pick from a short list of ranked tempo candidates (or set the BPM manually, or use the tap tempo button)
- Click "Generate tab" to run pitch detection, fretboard mapping, rhythm quantization, and tab rendering
- The result is displayed as a 4-line ASCII tab broken into bars, with a horizontal scrollbar for longer recordings
- Note durations are visible in the tab: a fret followed by `=` means the note is still ringing, while `-` is silence or a rest, so `5=======` is a held note and `5-` is a short one
- Play the result back as MIDI to check by ear whether it matches the recording

Pitch and fret accuracy is solid: detection is constrained to the bass range and harmonic ghost notes are filtered out. Rhythm is accurate once the BPM is roughly correct, since the tempo is then refined to fit the detected onsets. A single automatic BPM guess is unreliable, so instead the app ranks several tempo candidates for you to choose from, and you can always set or tap the tempo.

What is not built yet: sheet music export, source separation for full mixes, live input.

## Background

This is partly a personal project. I play bass myself, and I am building Bassova mainly because I want a tool like this for my own playing. If it ends up being useful to other bass players too, that is a nice bonus.

## Roadmap

- [x] Pitch and onset detection on an isolated bass recording
- [x] Fretboard mapping to standard 4-string bass
- [x] ASCII tab output broken into bars
- [x] Note durations and rests shown in the tab
- [x] Desktop app with file picker, BPM detection, and tap tempo
- [x] Ranked tempo candidate picker
- [x] Rhythm quantization with offset correction and tempo fitting
- [x] MIDI playback to check the result by ear
- [x] Accuracy benchmark against synthetic ground truth
- [ ] Sheet music export (MusicXML)
- [ ] Source separation for full band recordings
- [ ] Live input mode
- [ ] Mobile app

## Tech stack

- Core engine: Python (librosa, basic-pitch, numpy, pretty_midi)
- Desktop UI: PySide6, with pygame for MIDI playback
- Accuracy benchmark: mir_eval
- Mobile UI: to be decided

## Getting started

Requires Python 3.11. Python 3.12 and 3.13 are not supported yet because TensorFlow (a dependency of Basic Pitch) does not support them.

```bash
git clone https://github.com/your-username/bassova.git
cd bassova
py -3.11 -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# or: venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
python ui/desktop/main.py
```

## Measuring accuracy

Transcription accuracy is tracked with a small benchmark. It renders known bass
lines to audio with a simple harmonic plucked-string synth, runs the detection
pipeline, and scores the result against the ground truth with mir_eval, reporting
note-level and onset F-measure per case plus an average:

```bash
python -m evaluation
```

Because the audio is synthetic, the numbers are a relative score for tuning and
catching regressions, not an absolute promise about real recordings. A real
recording paired with a ground-truth note list can be added as a new case to
measure that too.

## Contributing

Not open for contributions yet. Feel free to open an issue with ideas or feedback.

## License

To be decided.
