from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Nozzle:
    throat_area_m2: float
    exit_area_m2: float

    @property
    def expansion_ratio(self) -> float:
        return self.exit_area_m2 / self.throat_area_m2

    def validate(self) -> None:
        if self.throat_area_m2 <= 0:
            raise ValueError("throat_area_m2 must be greater than 0")

        if self.exit_area_m2 <= 0:
            raise ValueError("exit_area_m2 must be greater than 0")

        if self.exit_area_m2 < self.throat_area_m2:
            raise ValueError("exit_area_m2 must be >= throat_area_m2")