from dataclasses import dataclass

from rocketcea.cea_obj import CEA_Obj


@dataclass(slots=True)
class ChamberProperties:
    gamma: float
    molecular_weight_kg_per_kmol: float
    chamber_temperature_k: float
    cstar_m_s: float
    isp_vac_s: float
    isp_sea_level_s: float


class RocketCEAAdapter:
    """Adapter for RocketCEA thermochemistry calculations.

    Keeps the application layer independent of RocketCEA internals.
    """

    def __init__(self, oxidizer: str, fuel: str, mixture_ratio: float | None = None) -> None:
        self._cea = CEA_Obj(oxName=oxidizer, fuelName=fuel)
        self._mixture_ratio = mixture_ratio

    def get_chamber_properties(
        self,
        chamber_pressure_pa: float,
        expansion_ratio: float,
    ) -> ChamberProperties:
        """Return chamber properties for a given pressure and expansion ratio."""
        pc_psia = chamber_pressure_pa / 6894.76  # Pa -> psia

        kwargs = {"Pc": pc_psia, "eps": expansion_ratio}
        if self._mixture_ratio is not None:
            kwargs["MR"] = self._mixture_ratio

        # RocketCEA returns: (IspVac, cstar, Tc, MW, gamma)
        isp_vac, cstar, tc, mw, gamma = self._cea.get_IvacCstrTc_ChmMwGam(
            **kwargs
        )

        # Convert units: Rankine -> Kelvin, ft/s -> m/s
        return ChamberProperties(
            gamma=float(gamma),
            molecular_weight_kg_per_kmol=float(mw),
            chamber_temperature_k=float(tc) * 5.0 / 9.0,
            cstar_m_s=float(cstar) * 0.3048,
            isp_vac_s=float(isp_vac),
            isp_sea_level_s=0.0,  # Not returned by this method
        )

    def get_performance_at_exit(
        self,
        chamber_pressure_pa: float,
        expansion_ratio: float,
    ) -> tuple[float, float, float]:
        """Return (exit_mach, exit_pressure_pa, exit_temperature_k)."""
        pc_psia = chamber_pressure_pa / 6894.76

        kwargs = {"Pc": pc_psia, "eps": expansion_ratio}
        if self._mixture_ratio is not None:
            kwargs["MR"] = self._mixture_ratio

        # RocketCEA returns exit Mach number
        mach = self._cea.get_MachNumber(**kwargs)

        # Exit pressure ratio and temperature
        # P_exit / P_chamber from isentropic relation
        gamma = self.get_chamber_properties(chamber_pressure_pa, expansion_ratio).gamma
        p_exit_pa = pc_psia * (1.0 + (gamma - 1.0) / 2.0 * mach**2.0) ** (
            -gamma / (gamma - 1.0)
        )
        p_exit_pa = p_exit_pa * 6894.76

        return float(mach), p_exit_pa, 0.0
