import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rise.infrastructure.cea.rocketcea_adapter import ChamberProperties


@dataclass(slots=True, frozen=True)
class ValidationResult:
    metric: str
    expected: float
    actual: float
    absolute_error: float
    percent_error: float
    passed: bool


@dataclass(slots=True, frozen=True)
class ValidationSummary:
    case_name: str
    results: list[ValidationResult]
    all_passed: bool


@dataclass(slots=True, frozen=True)
class TransientValidationResult:
    metric: str
    rms_error: float
    max_error: float
    mean_error: float
    passed: bool


@dataclass(slots=True, frozen=True)
class TransientValidationSummary:
    case_name: str
    results: list[TransientValidationResult]
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
    def _load_reference(path: str | Path) -> dict[str, Any]:
        with open(path) as f:
            data: dict[str, Any] = json.load(f)
            return data

    def validate(self, props: ChamberProperties) -> ValidationSummary:
        """Compare ChamberProperties (steady-state) against reference values."""
        expected = self._reference["expected_values"]
        tolerance = self._reference["tolerance"]

        results: list[ValidationResult] = []
        all_passed = True

        for metric, expected_value in expected.items():
            actual_value = getattr(props, metric, None)
            if actual_value is None:
                continue

            absolute_error = abs(actual_value - expected_value)
            percent_error = absolute_error / abs(expected_value) * 100.0
            passed = percent_error <= tolerance.get(metric, 5.0)
            if not passed:
                all_passed = False

            results.append(
                ValidationResult(
                    metric=metric,
                    expected=expected_value,
                    actual=actual_value,
                    absolute_error=absolute_error,
                    percent_error=percent_error,
                    passed=passed,
                )
            )

        return ValidationSummary(
            case_name=self._reference["name"],
            results=results,
            all_passed=all_passed,
        )

    def validate_steady_state(
        self,
        thrust_n: float,
        specific_impulse_s: float,
        chamber_pressure_pa: float,
    ) -> ValidationSummary:
        """Compare steady-state performance against reference."""
        tolerance = self._reference["tolerance"]
        expected = self._reference["expected_values"]

        results: list[ValidationResult] = []
        all_passed = True

        metrics = [
            ("thrust_n", thrust_n),
            ("specific_impulse_s", specific_impulse_s),
            ("chamber_pressure_pa", chamber_pressure_pa),
        ]

        for metric, actual in metrics:
            expected_value = expected.get(metric)
            if expected_value is None:
                continue

            absolute_error = abs(actual - expected_value)
            percent_error = absolute_error / abs(expected_value) * 100.0
            passed = percent_error <= tolerance.get(metric, 5.0)
            if not passed:
                all_passed = False

            results.append(
                ValidationResult(
                    metric=metric,
                    expected=expected_value,
                    actual=actual,
                    absolute_error=absolute_error,
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
        time_s: list[float],
        reference_pressure_pa: list[float] | None = None,
        reference_thrust_n: list[float] | None = None,
        actual_pressure_pa: list[float] | None = None,
        actual_thrust_n: list[float] | None = None,
    ) -> TransientValidationSummary:
        """Compare transient curves using RMS error.

        If reference time-series data is provided, compute RMS error.
        Otherwise, only check that the initial conditions match.
        """
        results: list[TransientValidationResult] = []
        all_passed = True

        # Check initial conditions
        expected_pc = self._reference["operating_conditions"]["chamber_pressure_pa"]
        if actual_pressure_pa:
            initial_error = abs((actual_pressure_pa[0] - expected_pc) / expected_pc) * 100.0
            passed = initial_error <= 2.0
            if not passed:
                all_passed = False
            results.append(
                TransientValidationResult(
                    metric="initial_chamber_pressure_pa",
                    rms_error=initial_error,
                    max_error=initial_error,
                    mean_error=initial_error,
                    passed=passed,
                )
            )

        # If both reference and actual time-series are provided, compute RMS
        if reference_pressure_pa and actual_pressure_pa:
            rms_error = self._rms_error(reference_pressure_pa, actual_pressure_pa)
            max_error = self._max_error(reference_pressure_pa, actual_pressure_pa)
            mean_error = self._mean_error(reference_pressure_pa, actual_pressure_pa)
            passed = rms_error <= 5.0
            if not passed:
                all_passed = False
            results.append(
                TransientValidationResult(
                    metric="chamber_pressure_pa_rms",
                    rms_error=rms_error,
                    max_error=max_error,
                    mean_error=mean_error,
                    passed=passed,
                )
            )

        if reference_thrust_n and actual_thrust_n:
            rms_error = self._rms_error(reference_thrust_n, actual_thrust_n)
            max_error = self._max_error(reference_thrust_n, actual_thrust_n)
            mean_error = self._mean_error(reference_thrust_n, actual_thrust_n)
            passed = rms_error <= 5.0
            if not passed:
                all_passed = False
            results.append(
                TransientValidationResult(
                    metric="thrust_n_rms",
                    rms_error=rms_error,
                    max_error=max_error,
                    mean_error=mean_error,
                    passed=passed,
                )
            )

        return TransientValidationSummary(
            case_name=self._reference["name"],
            results=results,
            all_passed=all_passed,
        )

    @staticmethod
    def _rms_error(reference: list[float], actual: list[float]) -> float:
        """Compute RMS percent error between two time-series."""
        n = min(len(reference), len(actual))
        squared_errors = [
            ((actual[i] - reference[i]) / reference[i]) ** 2
            for i in range(n)
            if reference[i] != 0
        ]
        if not squared_errors:
            return 0.0
        return math.sqrt(sum(squared_errors) / len(squared_errors)) * 100.0

    @staticmethod
    def _max_error(reference: list[float], actual: list[float]) -> float:
        """Compute maximum absolute percent error."""
        n = min(len(reference), len(actual))
        errors = [
            abs((actual[i] - reference[i]) / reference[i]) * 100.0
            for i in range(n)
            if reference[i] != 0
        ]
        return max(errors) if errors else 0.0

    @staticmethod
    def _mean_error(reference: list[float], actual: list[float]) -> float:
        """Compute mean absolute percent error."""
        n = min(len(reference), len(actual))
        errors = [
            abs((actual[i] - reference[i]) / reference[i]) * 100.0
            for i in range(n)
            if reference[i] != 0
        ]
        return sum(errors) / len(errors) if errors else 0.0

    def generate_report(
        self,
        steady_summary: ValidationSummary,
        transient_summary: TransientValidationSummary,
        output_path: str | Path,
    ) -> None:
        """Generate a markdown validation report.

        Shows predicted value, reference value, error, and pass/fail
        for each metric in a clear engineering review format.
        """
        lines = [
            f"# Validation Report: {steady_summary.case_name}",
            "",
            f"**Reference Source:** {self._reference['source']}",
            "",
            "## Steady-State Validation",
            "",
            "| Metric | Predicted | Reference | Abs. Error | % Error | Pass/Fail |",
            "|--------|-----------|-----------|------------|---------|-----------|",
        ]

        for r in steady_summary.results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(
                f"| {r.metric} | {r.actual:.4f} | {r.expected:.4f} | "
                f"{r.absolute_error:.4f} | {r.percent_error:.2f}% | {status} |"
            )

        lines.append("")
        lines.append(
            f"**Steady-State Overall:** {'PASS' if steady_summary.all_passed else 'FAIL'}"
        )
        lines.append("")
        lines.append("## Transient Validation")
        lines.append("")
        lines.append(
            "| Metric | RMS Error | Max Error | Mean Error | Pass/Fail |"
        )
        lines.append(
            "|--------|-----------|-----------|------------|-----------|"
        )

        for tr in transient_summary.results:
            status = "PASS" if tr.passed else "FAIL"
            lines.append(
                f"| {tr.metric} | {tr.rms_error:.2f}% | {tr.max_error:.2f}% | "
                f"{tr.mean_error:.2f}% | {status} |"
            )

        lines.append("")
        lines.append(
            f"**Transient Overall:** {'PASS' if transient_summary.all_passed else 'FAIL'}"
        )
        lines.append("")
        lines.append(
            f"**Final Verdict:** {'PASS' if (steady_summary.all_passed and transient_summary.all_passed) else 'FAIL'}"
        )

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

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
