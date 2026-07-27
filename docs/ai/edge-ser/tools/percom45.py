"""45-feature acoustic schema aligned with the PerCom reference workflow.

The feature families and aggregation match the upstream ``extractor.py`` used
by the reference implementation: 13 scalar/prosodic features, 13 MFCC means,
12 chroma means, and 7 spectral-contrast means.  Audio keeps its native sample
rate, matching the original Python extractor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

N_FFT = 2_048
HOP_LENGTH = 512
N_MFCC = 13
FEATURE_SCHEMA_VERSION = "percom45-v1"

FEATURE_NAMES = (
    "energy",
    "zero_crossing_rate",
    "f0",
    "f2",
    "jitter",
    "shimmer",
    "band_energy_ratio",
    "pause_rate",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff",
    "spectral_flux",
    "spectral_flatness",
    *(f"mfcc_{index}" for index in range(1, 14)),
    *(f"chroma_{index}" for index in range(1, 13)),
    *(f"spectral_contrast_{index}" for index in range(1, 8)),
)


@dataclass(frozen=True)
class PerComFeatureVector:
    values: np.ndarray
    sample_rate_hz: int
    duration_seconds: float


def _finite_mean(values: np.ndarray) -> float:
    finite_values = values[np.isfinite(values)]
    return float(np.mean(finite_values)) if finite_values.size else 0.0


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    """Decode MP3/WAV/etc. to mono PCM without resampling."""
    samples, sample_rate = librosa.load(path, sr=None, mono=True)
    if samples.size < N_FFT:
        raise ValueError(f"{path} is too short: need at least {N_FFT} samples")
    return samples.astype(np.float32), sample_rate


def extract_features(path: Path) -> PerComFeatureVector:
    """Return the 45-dimensional PerCom-style feature vector."""
    samples, sample_rate = load_audio(path)
    mfcc = librosa.feature.mfcc(
        y=samples,
        sr=sample_rate,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
    )
    chroma = librosa.feature.chroma_stft(
        y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
    )
    contrast = librosa.feature.spectral_contrast(
        y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
    )
    pitches, _ = librosa.piptrack(
        y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
    )
    harmonic = librosa.effects.hpss(samples)[0]
    harmonic_pitches, _ = librosa.piptrack(
        y=harmonic, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
    )
    frames = librosa.util.frame(samples, frame_length=N_FFT, hop_length=HOP_LENGTH)
    frame_rms = np.sqrt(np.mean(np.square(frames), axis=0))

    mfcc_zero = librosa.util.normalize(mfcc[0])
    values = np.asarray(
        [
            _finite_mean(librosa.feature.rms(y=samples)),
            _finite_mean(librosa.feature.zero_crossing_rate(samples)),
            _finite_mean(pitches[pitches > 0]),
            _finite_mean(harmonic_pitches[harmonic_pitches > 0]),
            _finite_mean(np.abs(np.diff(mfcc_zero))),
            _finite_mean(np.abs(np.diff(samples))),
            _finite_mean(
                librosa.feature.spectral_bandwidth(
                    y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
                )
            ),
            float(np.mean(frame_rms < 0.01)),
            _finite_mean(
                librosa.feature.spectral_centroid(
                    y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
                )
            ),
            _finite_mean(
                librosa.feature.spectral_bandwidth(
                    y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
                )
            ),
            _finite_mean(
                librosa.feature.spectral_rolloff(
                    y=samples,
                    sr=sample_rate,
                    n_fft=N_FFT,
                    hop_length=HOP_LENGTH,
                    roll_percent=0.85,
                )
            ),
            _finite_mean(
                librosa.onset.onset_strength(
                    y=samples, sr=sample_rate, n_fft=N_FFT, hop_length=HOP_LENGTH
                )
            ),
            _finite_mean(librosa.feature.spectral_flatness(y=samples, n_fft=N_FFT)),
            *np.mean(mfcc, axis=1),
            *np.mean(chroma, axis=1),
            *np.mean(contrast, axis=1),
        ],
        dtype=np.float32,
    )
    if values.shape != (45,) or not np.isfinite(values).all():
        raise ValueError(f"{path} did not produce 45 finite PerCom features")
    return PerComFeatureVector(
        values=values,
        sample_rate_hz=sample_rate,
        duration_seconds=samples.size / sample_rate,
    )
