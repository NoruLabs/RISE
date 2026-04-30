from dataclasses import dataclass
from rise.domain.entities.nozzle import Nozzle
from rise.domain.value_objects.operating_point import OperatingPoint
from rise.domain.services.thrust_service import (
    compute_specific_impulse,
    compute_thrust,
)


@dataclass(slots=True)
class Engine:
    name: str
    nozzle: Nozzle
    operating_point: OperatingPoint

    def compute_thrust(self) -> float:
        """Compute engine thrust using the domain service."""
        return compute_thrust(self.nozzle, self.operating_point)

    def compute_specific_impulse(self) -> float:
        """Compute engine specific impulse using the domain service."""
        return compute_specific_impulse(self.nozzle, self.operating_point)

    def validate(self) -> None:
        """Validate all engine components."""
        self.nozzle.validate()
        self.operating_point.validate()