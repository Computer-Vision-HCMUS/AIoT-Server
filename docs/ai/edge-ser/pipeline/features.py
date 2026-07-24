"""Shared, deterministic audio features for RAVDESS training and MP3 inference."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

SAMPLE_RATE_HZ = 22_050
N_FFT = 2_048
HOP_LENGTH = 512
N_MFCC = 40


@dataclass(frozen=True)
class FeatureVector:
    values: np.ndarray
    sample_rate_hz: int
    duration_seconds: float


def _mean_and_std(values: np.ndarray) -> np.ndarray:
    """Return stable summary statistics over the final (frame) axis."""
    return np.concatenate(
        [
            np.mean(values, axis=-1).reshape(-1),
            np.std(values, axis=-1).reshape(-1),
        ]
    ).astype(np.float32)


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    """Decode WAV/MP3/etc. into mono PCM at the model's fixed sample rate."""
    samples, sample_rate = librosa.load(path, sr=SAMPLE_RATE_HZ, mono=True)
    if samples.size < N_FFT:
        raise ValueError(f"{path} is too short: need at least {N_FFT} samples")
    return samples.astype(np.float32), sample_rate


def extract_features(path: Path) -> FeatureVector:
    """Extract fixed-size acoustic features from a supported audio file."""
    samples, sample_rate = load_audio(path)
    stft = np.abs(
        librosa.stft(samples, n_fft=N_FFT, hop_length=HOP_LENGTH, window="hann")
    )

    mfcc = librosa.feature.mfcc(
        y=samples,
        sr=sample_rate,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
    )
    delta = librosa.feature.delta(mfcc)
    chroma = librosa.feature.chroma_stft(S=stft, sr=sample_rate)
    contrast = librosa.feature.spectral_contrast(S=stft, sr=sample_rate)

    scalar_features = [
        librosa.feature.rms(S=stft),
        librosa.feature.zero_crossing_rate(samples, hop_length=HOP_LENGTH),
        librosa.feature.spectral_centroid(S=stft, sr=sample_rate),
        librosa.feature.spectral_bandwidth(S=stft, sr=sample_rate),
        librosa.feature.spectral_rolloff(S=stft, sr=sample_rate, roll_percent=0.85),
        librosa.feature.spectral_flatness(S=stft),
    ]

    values = np.concatenate(
        [
            _mean_and_std(mfcc),
            _mean_and_std(delta),
            _mean_and_std(chroma),
            _mean_and_std(contrast),
            *(_mean_and_std(feature) for feature in scalar_features),
        ]
    )
    if not np.isfinite(values).all():
        raise ValueError(f"{path} produced non-finite audio features")

    return FeatureVector(
        values=values,
        sample_rate_hz=sample_rate,
        duration_seconds=samples.size / sample_rate,
    )
