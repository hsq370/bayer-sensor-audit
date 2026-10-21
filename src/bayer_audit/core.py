"""Numerical summaries for single Bayer frames and aligned repeat captures."""

from __future__ import annotations

from typing import Any

import numpy as np

CFA_LAYOUTS: dict[str, tuple[tuple[str, str], tuple[str, str]]] = {
    "RGGB": (("R", "G1"), ("G2", "B")),
    "BGGR": (("B", "G1"), ("G2", "R")),
    "GRBG": (("G1", "R"), ("B", "G2")),
    "GBRG": (("G1", "B"), ("R", "G2")),
}


def _frame_array(frame: Any, name: str) -> np.ndarray:
    array = np.asarray(frame)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a 2D single-plane Bayer array; got shape {array.shape}")
    if array.size == 0:
        raise ValueError(f"{name} must not be empty")
    if array.shape[0] < 2 or array.shape[1] < 2:
        raise ValueError(f"{name} must be at least 2x2 to contain all Bayer CFA sites")
    if array.dtype.kind not in "uif":
        raise ValueError(f"{name} must have an unsigned, signed integer, or floating dtype")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains NaN or infinite values")
    return array


def _layout(cfa: str) -> tuple[tuple[str, str], tuple[str, str]]:
    key = cfa.upper()
    if key not in CFA_LAYOUTS:
        choices = ", ".join(CFA_LAYOUTS)
        raise ValueError(f"Unsupported CFA layout {cfa!r}; choose one of: {choices}")
    return CFA_LAYOUTS[key]


def _stats(values: np.ndarray) -> dict[str, int | float]:
    return {
        "samples": int(values.size),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values, dtype=np.float64)),
        "std_population": float(np.std(values, dtype=np.float64)),
        "median": float(np.median(values)),
    }


def _channels(array: np.ndarray, layout: tuple[tuple[str, str], tuple[str, str]]) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    for row in range(2):
        for col in range(2):
            result[layout[row][col]] = array[row::2, col::2]
    return result


def audit_frame(
    frame: Any,
    *,
    cfa: str = "RGGB",
    black_level: float | None = None,
    saturation_level: float | None = None,
) -> dict[str, Any]:
    """Summarize a 2D Bayer frame without inferring sensor calibration."""
    array = _frame_array(frame, "frame")
    layout = _layout(cfa)
    if black_level is not None and not np.isfinite(black_level):
        raise ValueError("black_level must be finite")
    if saturation_level is not None and not np.isfinite(saturation_level):
        raise ValueError("saturation_level must be finite")
    if black_level is not None and saturation_level is not None and black_level > saturation_level:
        raise ValueError("black_level must be less than or equal to saturation_level")

    report: dict[str, Any] = {
        "kind": "single_frame_audit",
        "shape": [int(v) for v in array.shape],
        "dtype": str(array.dtype),
        "cfa": cfa.upper(),
        "cfa_tile": [list(row) for row in layout],
        "frame": _stats(array),
        "channels": {name: _stats(values) for name, values in _channels(array, layout).items()},
    }
    if black_level is not None:
        count = int(np.count_nonzero(array <= black_level))
        report["black_level"] = {
            "threshold": float(black_level),
            "count_at_or_below": count,
            "fraction_at_or_below": float(count / array.size),
        }
    if saturation_level is not None:
        count = int(np.count_nonzero(array >= saturation_level))
        report["saturation_level"] = {
            "threshold": float(saturation_level),
            "count_at_or_above": count,
            "fraction_at_or_above": float(count / array.size),
        }
    return report


def compare_repeat_frames(
    first: Any,
    second: Any,
    *,
    cfa: str = "RGGB",
) -> dict[str, Any]:
    """Estimate repeat-frame difference statistics for registered captures.

    Under the equal, independent noise assumption, std(second-first)/sqrt(2)
    estimates per-frame temporal noise. Scene changes and registration error
    also contribute to the measured difference.
    """
    a = _frame_array(first, "first")
    b = _frame_array(second, "second")
    if a.shape != b.shape:
        raise ValueError(f"Frames must have identical shapes; got {a.shape} and {b.shape}")
    layout = _layout(cfa)
    difference = b.astype(np.float64) - a.astype(np.float64)
    sigma = float(np.std(difference, dtype=np.float64) / np.sqrt(2.0))
    report: dict[str, Any] = {
        "kind": "repeat_frame_noise_audit",
        "shape": [int(v) for v in a.shape],
        "dtype_first": str(a.dtype),
        "dtype_second": str(b.dtype),
        "cfa": cfa.upper(),
        "assumptions": [
            "The frames show the same scene and are spatially registered.",
            "Per-pixel noise is independent between captures and has equal variance.",
            "The estimate includes any scene, illumination, or registration changes in the frame difference.",
        ],
        "difference_second_minus_first": _stats(difference),
        "per_frame_temporal_noise_std_estimate": sigma,
        "channels": {},
    }
    for name, values in _channels(difference, layout).items():
        report["channels"][name] = {
            "difference": _stats(values),
            "per_frame_temporal_noise_std_estimate": float(np.std(values, dtype=np.float64) / np.sqrt(2.0)),
        }
    return report
