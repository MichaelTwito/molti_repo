import unittest
from pathlib import Path

from pydantic import ValidationError

from projects.promptprecision.taskspec import load_taskspec_v1, validate_taskspec_v1


class TestTaskSpecV1(unittest.TestCase):
    def _base_data(self) -> dict:
        return {
            "task_id": "t",
            "task_version": "1.0.0",
            "base_model_id": "m",
            "system_prompt": "s",
            "instruction_template": "i",
            "io_schema": {},
            "rubric": {},
            "eval_split": {"strategy": "random"},
        }

    def test_example_file_validates(self) -> None:
        p = Path(__file__).resolve().parents[1] / "specs" / "examples" / "invoice-mvp.taskspec.json"
        spec = load_taskspec_v1(p)
        self.assertEqual(spec.task_id, "invoice_mvp_extract_v1")
        self.assertEqual(spec.eval_split.strategy, "random")

    def test_forbids_unknown_fields(self) -> None:
        data = self._base_data()
        data["nope"] = 123
        with self.assertRaises(ValidationError):
            validate_taskspec_v1(data)

    def test_task_version_must_be_semver(self) -> None:
        data = self._base_data()
        data["task_version"] = "1"
        with self.assertRaises(ValidationError):
            validate_taskspec_v1(data)

    def test_eval_split_no_ratios_is_ok(self) -> None:
        data = self._base_data()
        spec = validate_taskspec_v1(data)
        self.assertIsNone(spec.eval_split.train_ratio)
        self.assertIsNone(spec.eval_split.val_ratio)
        self.assertIsNone(spec.eval_split.test_ratio)

    def test_eval_split_partial_ratios_fail(self) -> None:
        data = self._base_data()
        data["eval_split"] = {"strategy": "random", "train_ratio": 0.8}
        with self.assertRaises(ValidationError):
            validate_taskspec_v1(data)

        data = self._base_data()
        data["eval_split"] = {"strategy": "random", "train_ratio": 0.8, "val_ratio": 0.1}
        with self.assertRaises(ValidationError):
            validate_taskspec_v1(data)

    def test_eval_split_ratios_must_sum_to_1(self) -> None:
        data = self._base_data()
        data["eval_split"] = {"strategy": "random", "train_ratio": 0.6, "val_ratio": 0.2, "test_ratio": 0.1}
        with self.assertRaises(ValidationError):
            validate_taskspec_v1(data)

    def test_eval_split_ratios_sum_to_1_pass(self) -> None:
        data = self._base_data()
        data["eval_split"] = {"strategy": "random", "train_ratio": 0.5, "val_ratio": 0.25, "test_ratio": 0.25}
        spec = validate_taskspec_v1(data)
        self.assertAlmostEqual(spec.eval_split.train_ratio or 0.0, 0.5)
        self.assertAlmostEqual(spec.eval_split.val_ratio or 0.0, 0.25)
        self.assertAlmostEqual(spec.eval_split.test_ratio or 0.0, 0.25)

    def test_eval_split_float_edge_case_isclose(self) -> None:
        # 0.1 + 0.2 + 0.7 is not exactly representable in binary floats.
        # Validation should accept this as "sums to 1" (within tolerance).
        data = self._base_data()
        data["eval_split"] = {"strategy": "random", "train_ratio": 0.1, "val_ratio": 0.2, "test_ratio": 0.7}
        validate_taskspec_v1(data)


if __name__ == "__main__":
    unittest.main()
