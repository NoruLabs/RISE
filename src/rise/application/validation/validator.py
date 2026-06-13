import json
from dataclasses import dataclass
from pathlib import Path

from rise.infrastructure.cea.rocketcea_adapter import ChamberProperties


@dataclass(slots=True)
class ValidationResult:
    metric: str
    expected: float
    actual: float
    percent_error: float
    passed: bool


@dataclass(slots=True)
class ValidationSummary:
    case_name: str
    results: list[ValidationResult]
    all_passed: bool


class Validator:
    """Compare simulation results against reference data.

    Loads a reference case from JSON and computes percent errors
    for each metric. Validation is a post-processing step that
    never modifies the simulation logic.
    """

    def __init__(self, reference_path: str | Path) -> None:
        self._reference = self._load_reference(reference_path)

    @staticmethod
    def _load_reference(path: str | Path) -> dict:
        with open(path, "r") as f:
            return json.load(f)

    def validate(self, props: ChamberProperties) -> ValidationSummary:
        """Compare ChamberProperties against reference values."""
        expected = self._reference["expected_values"]
        tolerance = self._reference["tolerance"]

        results: list[ValidationResult] = []
        all_passed = True

        for metric, expected_value in expected.items():
            actual_value = getattr(props, metric, None)
            if actual_value is None:
                continue

            percent_error = abs((actual_value - expected_value) / expected_value) * 100.0
            passed = percent_error <= tolerance[metric]
            if not passed:
                all_passed = False

            results.append(
                ValidationResult(
                    metric=metric,
                    expected=expected_value,
                    actual=actual_value,
                    percent_error=percent_error,
                    passed=passed,
                )
            )

        return ValidationSummary(
            case_name=self._reference["name"],
            results=results,
            all_passed=all_passed,
        )

    def validate_transient(
        self,
        initial_pressure_pa: float,
        final_pressure_pa: float,
        initial_thrust_n: float,
        final_thrust_n: float,
        initial_isp_s: float,
        final_isp_s: float,
    ) -> ValidationSummary:
        """Compare transient initial values against reference conditions.

        Checks that the initial chamber pressure matches the reference
        operating condition (within 0.1%).
        """
        expected_pc = self._reference["operating_conditions"]["chamber_pressure_pa"]
        results: list[ValidationResult] = []

        # Check initial chamber pressure
        error = abs((initial_pressure_pa - expected_pc) / expected_pc) * 100.0
        passed = error <= 0.1
        results.append(
            ValidationResult(
                metric="initial_chamber_pressure_pa",
                expected=expected_pc,
                actual=initial_pressure_pa,
                percent_error=error,
                passed=passed,
            )
        )

        return ValidationSummary(
            case_name=self._reference["name"],
            results=results,
            all_passed=passed,
        )

    def print_summary(self, summary: ValidationSummary) -> str:
        """Return a formatted validation summary string."""
        lines = [
            f"Validation: {summary.case_name}",
            "",
        ]
        for r in summary.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(
                f"  {r.metric:30s} expected={r.expected:12.4f} "
                f"actual={r.actual:12.4f} error={r.percent_error:6.2f}% [{status}]"
            )
        lines.append("")
        lines.append(
            f"Overall: {'PASS' if summary.all_passed else 'FAIL'}"
        )
        return "\n".join(lines)
