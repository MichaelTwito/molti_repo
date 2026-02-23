from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvalSplitV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy: Literal["random"]
    train_ratio: Optional[float] = Field(default=None, ge=0, le=1)
    val_ratio: Optional[float] = Field(default=None, ge=0, le=1)
    test_ratio: Optional[float] = Field(default=None, ge=0, le=1)
    seed: Optional[int] = None

    @model_validator(mode="after")
    def _validate_ratios(self) -> "EvalSplitV1":
        """Ensure split ratios are either all omitted or all present and sum to 1.

        Rules:
        - If none of train_ratio/val_ratio/test_ratio are provided: OK (implementation default).
        - If any ratio is provided: all three must be provided.
        - When provided, ratios must sum to 1.0 (within tolerance).
        """

        ratios = {
            "train_ratio": self.train_ratio,
            "val_ratio": self.val_ratio,
            "test_ratio": self.test_ratio,
        }
        provided = {k: v for k, v in ratios.items() if v is not None}
        if not provided:
            return self

        missing = [k for k, v in ratios.items() if v is None]
        if missing:
            missing_str = ", ".join(missing)
            raise ValueError(
                "If any of train_ratio/val_ratio/test_ratio are provided, all three must be provided. "
                f"Missing: {missing_str}."
            )

        total = float(self.train_ratio) + float(self.val_ratio) + float(self.test_ratio)
        # tolerate floating point representation (e.g. 0.1 + 0.2 + 0.7)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                "train_ratio + val_ratio + test_ratio must sum to 1.0 "
                f"(got {total})."
            )

        return self


class ExampleV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_text: str
    output_json: Dict[str, Any]


class TaskSpecV1(BaseModel):
    """Pydantic implementation of `specs/taskspec.v1.schema.json`.

    Notes:
    - `io_schema` is stored inline as a JSON object (draft is task-defined).
    - `rubric` is intentionally free-form for MVP.
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    task_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    base_model_id: str = Field(min_length=1)

    system_prompt: str = Field(min_length=1)
    instruction_template: str = Field(min_length=1)

    io_schema: Dict[str, Any]
    label_enums: Dict[str, List[str]] = Field(default_factory=dict)
    rubric: Dict[str, Any]

    eval_split: EvalSplitV1
    example: Optional[ExampleV1] = None


def validate_taskspec_v1(data: Mapping[str, Any]) -> TaskSpecV1:
    """Validate and coerce a TaskSpec (v1).

    Raises:
        pydantic.ValidationError
    """

    # pydantic will deep-validate nested models and forbid unknown fields.
    return TaskSpecV1.model_validate(dict(data))


def load_taskspec_v1(path: str | Path) -> TaskSpecV1:
    """Load and validate a TaskSpec JSON file."""

    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"TaskSpec root must be an object, got {type(data).__name__}")
    return validate_taskspec_v1(data)
