"""File loading for formats that preserve a single 2D array."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_frame(path: str | Path, *, key: str | None = None) -> np.ndarray:
    """Load .npy, .npz, or (with the optional extra) TIFF into a 2D array."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in {".npy", ".npz"}:
        loaded = np.load(source, allow_pickle=False)
        if isinstance(loaded, np.lib.npyio.NpzFile):
            try:
                names = loaded.files
                if key is None:
                    if len(names) != 1:
                        raise ValueError(f"{source} contains multiple arrays; specify --key from: {', '.join(names)}")
                    key_to_read = names[0]
                else:
                    if key not in names:
                        raise ValueError(f"Array {key!r} not found in {source}; available: {', '.join(names)}")
                    key_to_read = key
                return np.asarray(loaded[key_to_read])
            finally:
                loaded.close()
        if key is not None:
            raise ValueError("--key is only valid for .npz files")
        return np.asarray(loaded)
    if suffix in {".tif", ".tiff"}:
        if key is not None:
            raise ValueError("--key is only valid for .npz files")
        try:
            import tifffile
        except ImportError as exc:
            raise RuntimeError("TIFF support requires the optional dependency: pip install bayer-sensor-audit[tiff]") from exc
        return np.asarray(tifffile.imread(source))
    raise ValueError("Supported input formats are .npy, .npz, and .tif/.tiff (optional dependency)")
