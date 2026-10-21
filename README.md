# Bayer Sensor Audit

A small Python CLI for two bounded checks on single-plane Bayer RAW arrays:

- per-frame and per-CFA-site value summaries, with optional counts at or beyond supplied black and saturation thresholds;
- a repeat-frame difference summary and a per-frame temporal-noise estimate under explicit equal-variance, independent-noise assumptions.

The tool does not infer camera metadata, calibrate a sensor, identify bad pixels, or prove optical or radiometric fidelity. A repeat-frame estimate is only meaningful when captures show the same static scene with matched settings and are spatially registered. Motion, illumination drift, clipping, demosaicing, or other preprocessing can bias it.

## Install

```powershell
python -m pip install .
```

For TIFF input:

```powershell
python -m pip install ".[tiff]"
```

For development and tests:

```powershell
python -m pip install ".[dev]"
python -m pytest
```

## Input formats

Inputs are 2D arrays stored as `.npy` or `.npz`; single-page TIFF is supported with the `tiff` extra. Multi-array `.npz` files require an array key. Vendor-specific `.raw` files are intentionally not guessed: decode them using verified width, height, bit depth, byte order, and packing metadata before auditing.

## Examples

Summarize one frame, naming its CFA order and known thresholds:

```powershell
bayer-audit inspect capture.npy --cfa RGGB --black-level 64 --saturation-level 4095 --output report.json
```

Estimate temporal noise from two matched, registered captures:

```powershell
bayer-audit noise repeat_a.npy repeat_b.npy --cfa RGGB --output noise-report.json
```

Generate a deterministic synthetic pair in `examples/` and run both commands:

```powershell
python examples/generate_demo.py
bayer-audit inspect examples/repeat_a.npy --cfa RGGB --black-level 0 --saturation-level 4095 --output examples/inspect-report.json
bayer-audit noise examples/repeat_a.npy examples/repeat_b.npy --cfa RGGB --output examples/noise-report.json
```

The reported noise estimate is `std(frame_b - frame_a) / sqrt(2)`. It estimates per-frame temporal noise only when the two captures have equal independent noise and an unchanged signal. The report also includes the observed frame difference so scene or registration changes are visible to the analyst.

## Development status

This is an initial, small utility. The first release focuses on transparent calculations, input validation, JSON output, and synthetic tests. Contributions that add a format or metric should include source-format assumptions and tests against known arrays.

## License

MIT. See [LICENSE](LICENSE).
