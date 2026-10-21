import unittest

import numpy as np

from bayer_audit import audit_frame, compare_repeat_frames


class AuditFrameTests(unittest.TestCase):
    def test_rggb_channel_mapping_and_threshold_counts(self):
        frame = np.array([[10, 20, 30, 40], [50, 60, 70, 80]], dtype=np.uint16)
        report = audit_frame(frame, cfa="RGGB", black_level=10, saturation_level=80)
        self.assertEqual(report["channels"]["R"]["mean"], 20.0)
        self.assertEqual(report["channels"]["G1"]["mean"], 30.0)
        self.assertEqual(report["channels"]["G2"]["mean"], 60.0)
        self.assertEqual(report["channels"]["B"]["mean"], 70.0)
        self.assertEqual(report["black_level"]["count_at_or_below"], 1)
        self.assertEqual(report["saturation_level"]["count_at_or_above"], 1)

    def test_all_cfa_patterns_cover_every_pixel_once(self):
        frame = np.arange(36, dtype=np.uint16).reshape(6, 6)
        for cfa in ("RGGB", "BGGR", "GRBG", "GBRG"):
            report = audit_frame(frame, cfa=cfa)
            self.assertEqual(sum(channel["samples"] for channel in report["channels"].values()), frame.size)

    def test_rejects_non_2d_and_incompatible_thresholds(self):
        with self.assertRaisesRegex(ValueError, "2D"):
            audit_frame(np.zeros((4, 4, 3)))
        with self.assertRaisesRegex(ValueError, "at least 2x2"):
            audit_frame(np.zeros((1, 4)))
        with self.assertRaisesRegex(ValueError, "less than or equal"):
            audit_frame(np.zeros((4, 4)), black_level=10, saturation_level=5)


class RepeatNoiseTests(unittest.TestCase):
    def test_identical_frames_have_zero_estimated_noise(self):
        frame = np.arange(64, dtype=np.uint16).reshape(8, 8)
        report = compare_repeat_frames(frame, frame.copy())
        self.assertEqual(report["per_frame_temporal_noise_std_estimate"], 0.0)

    def test_independent_gaussian_noise_estimate_is_close_to_sigma(self):
        rng = np.random.default_rng(11)
        signal = np.full((512, 512), 1000.0)
        first = signal + rng.normal(0.0, 4.0, signal.shape)
        second = signal + rng.normal(0.0, 4.0, signal.shape)
        report = compare_repeat_frames(first, second)
        self.assertAlmostEqual(report["per_frame_temporal_noise_std_estimate"], 4.0, delta=0.08)

    def test_rejects_shape_mismatch(self):
        with self.assertRaisesRegex(ValueError, "identical shapes"):
            compare_repeat_frames(np.zeros((4, 4)), np.zeros((4, 6)))


if __name__ == "__main__":
    unittest.main()
