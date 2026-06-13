import numpy as np
import librosa


def load_audio(path, sr=22050):
    audio, sample_rate = librosa.load(path, sr=sr, mono=True)
    return audio, sample_rate


def detect_bpm(path):
    audio, sr = load_audio(path)

    # high-pass preemphasis removes dominant bass frequencies that
    # mislead beat tracking on bass-heavy recordings
    audio_hpf = librosa.effects.preemphasis(audio, coef=0.97)

    onset_env = librosa.onset.onset_strength(
        y=audio_hpf, sr=sr, aggregate=np.median
    )

    t1 = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)
    t2, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    t3 = librosa.feature.tempo(y=audio, sr=sr)

    candidates = [float(np.atleast_1d(t)[0]) for t in (t1, t2, t3)]

    # fold half-time / double-time outliers toward the median
    median = sorted(candidates)[1]
    folded = []
    for t in candidates:
        while t > median * 1.4:
            t /= 2
        while t < median * 0.7:
            t *= 2
        folded.append(t)

    return round(sum(folded) / len(folded))
