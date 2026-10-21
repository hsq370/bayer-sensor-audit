import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from bayer_audit.cli import main
from bayer_audit.io import load_frame


class InputTests(unittest.TestCase):
    def test_loads_npy_without_changing_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "frame.npy"
            expected = np.arange(16, dtype=np.uint16).reshape(4, 4)
            np.save(path, expected)
            np.testing.assert_array_equal(load_frame(path), expected)

    def test_npz_requires_key_when_multiple_arrays_are_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "frames.npz"
            np.savez(path, first=np.ones((4, 4)), second=np.zeros((4, 4)))
            with self.assertRaisesRegex(ValueError, "specify --key"):
                load_frame(path)
            np.testing.assert_array_equal(load_frame(path, key="second"), np.zeros((4, 4)))


class CliTests(unittest.TestCase):
    def test_inspect_emits_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "frame.npy"
            np.save(path, np.arange(16, dtype=np.uint16).reshape(4, 4))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = main(["inspect", str(path), "--cfa", "RGGB"])
            self.assertEqual(status, 0)
            self.assertEqual(json.loads(stdout.getvalue())["kind"], "single_frame_audit")

    def test_invalid_input_returns_user_facing_error(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = main(["inspect", "missing.npy"])
        self.assertEqual(status, 2)
        self.assertIn("bayer-audit: error:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
