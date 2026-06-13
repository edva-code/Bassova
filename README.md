# Bassova

Bassova is an app that turns music, recorded and eventually live, into bass guitar tabs and sheet music.

## What it does

Bassova listens to a bass part (either an isolated recording or a full mix) and automatically transcribes it into:

- Tablature (tab): mapped to a standard 4 string bass fretboard
- Sheet music: standard notation with rhythm and key signature

The goal is to make learning, transcribing, or documenting bass lines faster, without doing it note by note by ear.

## Why bass

Automatic music transcription is a hard, well known problem in general, but bass is one of the more tractable starting points. Bass parts are usually monophonic (one note at a time), played in a well defined low frequency range, which makes pitch detection significantly more reliable than for full polyphonic mixes.

## How it works (planned pipeline)

1. Audio input: a recorded file, or eventually a live stream
2. Source separation (for full mix recordings): isolate the bass from drums, guitars, and vocals
3. Pitch and onset detection: identify which notes are played and when
4. Rhythm quantization: align note timings to a musical grid (tempo, beats, bars)
5. Fretboard mapping: choose a string and fret for each note
6. Notation output: render as tab and/or standard sheet music (MusicXML)

## Status

Early planning stage. No working code yet. Architecture and roadmap are being defined before implementation starts.

## Background

This is partly a personal project. I play bass myself, and I am building Bassova mainly because I want a tool like this for my own playing. If it ends up being useful to other bass players too, that is a nice bonus.

## Roadmap

1. Core pipeline: pitch and onset detection on a clean, isolated bass recording, producing a basic tab output
2. Notation: rhythm quantization and export to standard sheet music (MusicXML)
3. Full mix support: source separation to isolate bass from a full band recording
4. Live mode: real time transcription from a live input
5. Desktop app, followed by a mobile app, built on the same core engine

## Planned tech stack

- Core engine: Python (librosa, basic-pitch, pretty_midi, music21)
- Desktop UI: PySide6
- Mobile UI: to be decided in a later phase

## Getting started

There is nothing to install yet. This section will be filled in once the first prototype is working.

## Contributing

Not open for contributions yet, the project is still in the planning phase. Feel free to open an issue with ideas or feedback once the repository has its first commits.

## License

To be decided.
