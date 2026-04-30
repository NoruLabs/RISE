import pytest

from rise.domain.entities.engine import Engine
from rise.domain.entities.nozzle import Nozzle
from rise.domain.value_objects.operating_point import OperatingPoint


@pytest.fixture
def valid_nozzle() -> Nozzle:
    return Nozzle(
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
    )


@pytest.fixture
def valid_operating_point() -> OperatingPoint:
    return OperatingPoint(
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )


@pytest.fixture
def valid_engine(valid_nozzle: Nozzle, valid_operating_point: OperatingPoint) -> Engine:
    return Engine(
        name="pressure-fed-test",
        nozzle=valid_nozzle,
        operating_point=valid_operating_point,
    )