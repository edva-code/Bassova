"""Basic audio loading helpers, used by the rest of the engine."""

import librosa


def load_audio(path, sr=22050):
    """Load an audio file as mono and resample it.

    Args:
        path: path to an audio file (wav, mp3, etc.)
        sr: target sample rate

    Returns:
        (audio, sample_rate): a 1D numpy array and the sample rate it is at
    """
    audio, sample_rate = librosa.load(path, sr=sr, mono=True)
    return audio, sample_rate
