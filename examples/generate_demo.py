"""Create a deterministic pair of synthetic 12-bit Bayer-like arrays."""

from pathlib import Path

import numpy as np


def main() -> None:
    output_dir = Path(__file__).parent
    rng = np.random.default_rng(2026)
    rows, cols = np.indices((96, 96))
    cfa_gain = np.where((rows % 2 == 0) & (cols % 2 == 0), 1.04, 1.0)
    cfa_gain = np.where((rows % 2 == 1) & (cols % 2 == 1), 0.96, cfa_gain)
    scene = 700.0 + 180.0 * cols / (cols.max() + 1) + 90.0 * rows / (rows.max() + 1)

    for name in ("repeat_a.npy", "repeat_b.npy"):
        captured = scene * cfa_gain + rng.normal(0.0, 6.0, scene.shape)
        np.save(output_dir / name, np.clip(captured, 0, 4095).astype(np.uint16))

    print(f"Wrote two synthetic uint16 arrays to {output_dir}")


if __name__ == "__main__":
    main()
