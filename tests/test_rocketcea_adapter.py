
from rise.infrastructure.cea.rocketcea_adapter import (
    ChamberProperties,
    RocketCEAAdapter,
)


def test_rocketcea_adapter_returns_chamber_properties() -> None:
    """The adapter should return sensible thermochemical properties for LOX/LH2."""
    adapter = RocketCEAAdapter("LOX", "LH2", mixture_ratio=4.0)
    props = adapter.get_chamber_properties(2_000_000.0, 6.0)

    assert isinstance(props, ChamberProperties)

    # gamma should be between 1.1 and 1.4
    assert 1.1 < props.gamma < 1.4

    # Molecular weight should be between 4 and 20 kg/kmol
    assert 4.0 < props.molecular_weight_kg_per_kmol < 20.0

    # Chamber temperature should be between 2000 and 4000 K
    assert 2000.0 < props.chamber_temperature_k < 4000.0

    # cstar should be between 1500 and 3000 m/s
    assert 1500.0 < props.cstar_m_s < 3000.0

    # Isp should be between 300 and 500 s
    assert 300.0 < props.isp_vac_s < 500.0
    assert 300.0 < props.isp_sea_level_s < 500.0

    # Vacuum Isp should be higher than sea level Isp
    assert props.isp_vac_s > props.isp_sea_level_s


def test_rocketcea_adapter_returns_exit_performance() -> None:
    """The adapter should return exit Mach and pressure."""
    adapter = RocketCEAAdapter("LOX", "LH2", mixture_ratio=4.0)
    mach, p_exit, _ = adapter.get_performance_at_exit(2_000_000.0, 6.0)

    # Exit Mach should be supersonic
    assert mach > 1.0

    # Exit pressure should be lower than chamber pressure
    assert p_exit < 2_000_000.0

    # Exit pressure should be positive
    assert p_exit > 0.0
