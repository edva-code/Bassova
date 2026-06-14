import numpy as np
import librosa

HOP_LENGTH = 512


def load_audio(path, sr=22050):
    audio, sample_rate = librosa.load(path, sr=sr, mono=True)
    return audio, sample_rate


def tempo_candidates(path, count=4, bpm_min=50, bpm_max=200):
    """Return a ranked list of plausible tempos (BPM) for the recording.

    Global tempo detection from bass alone is unreliable, and the common failure
    is locking onto a related tempo (half, double, or a subdivision) instead of
    the real beat. Rather than commit to one guess, we score every tempo in range
    by the autocorrelation of the onset envelope, reinforced across a few harmonics
    so the true beat tends to outscore its own subdivisions, then return the
    strongest distinct peaks for the user to choose from.
    """
    audio, sr = load_audio(path)

    # high-pass preemphasis removes the dominant low end that otherwise misleads
    # onset detection on bass-heavy recordings
    audio_hpf = librosa.effects.preemphasis(audio, coef=0.97)
    onset_env = librosa.onset.onset_strength(
        y=audio_hpf, sr=sr, hop_length=HOP_LENGTH, aggregate=np.median
    )

    ac = librosa.autocorrelate(onset_env)
    seconds_per_frame = HOP_LENGTH / sr

    grid = np.arange(bpm_min, bpm_max + 0.5, 0.5)
    scores = np.zeros(len(grid))
    for i, bpm in enumerate(grid):
        lag = (60.0 / bpm) / seconds_per_frame
        total = 0.0
        for harmonic in range(1, 5):  # the beat plus a few of its multiples
            offset = int(round(harmonic * lag))
            if 0 < offset < len(ac):
                total += ac[offset] / harmonic
        scores[i] = total

    # local maxima of the score curve are the candidate tempos
    peaks = [
        (grid[i], scores[i])
        for i in range(1, len(scores) - 1)
        if scores[i] >= scores[i - 1] and scores[i] > scores[i + 1]
    ]
    if not peaks:
        peaks = [(grid[int(np.argmax(scores))], float(scores.max()))]
    peaks.sort(key=lambda p: p[1], reverse=True)

    # drop peaks within ~3 percent of one we already kept
    chosen = []
    for bpm, _ in peaks:
        if all(abs(bpm - kept) / kept > 0.03 for kept in chosen):
            chosen.append(round(bpm))
        if len(chosen) >= count:
            break

    return chosen or [120]


def detect_bpm(path):
    """Single best tempo guess. Kept for callers that want one value."""
    return tempo_candidates(path, count=1)[0]
