from dataclasses import dataclass

from rocketcea.cea_obj import CEA_Obj

# Unit conversion constants
_PA_TO_PSIA = 1.0 / 6894.757293168
_PSIA_TO_PA = 6894.757293168
_RANKINE_TO_KELVIN = 5.0 / 9.0
_FT_S_TO_M_S = 0.3048


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

    RocketCEA uses English units (psia, Rankine, ft/s). This adapter
    converts all inputs to English, calls RocketCEA, then converts
    outputs back to SI so the application layer never sees psia or
    Rankine.
    """

    def __init__(self, oxidizer: str, fuel: str, mixture_ratio: float | None = None) -> None:
        self._cea = CEA_Obj(oxName=oxidizer, fuelName=fuel)
        self._mixture_ratio = mixture_ratio

    def _build_kwargs(self, pc_psia: float, eps: float) -> dict:
        """Build the keyword argument dict for RocketCEA calls."""
        kwargs = {"Pc": pc_psia, "eps": eps}
        if self._mixture_ratio is not None:
            kwargs["MR"] = self._mixture_ratio
        return kwargs

    def get_chamber_properties(
        self,
        chamber_pressure_pa: float,
        expansion_ratio: float,
    ) -> ChamberProperties:
        """Return chamber properties for a given pressure and expansion ratio.

        All inputs are SI (Pa, dimensionless). All outputs are SI
        (K, kg/kmol, m/s, s).
        """
        # 1. Convert SI -> English
        pc_psia = chamber_pressure_pa * _PA_TO_PSIA

        # 2. Call RocketCEA
        kwargs = self._build_kwargs(pc_psia, expansion_ratio)
        isp_vac, cstar, tc, mw, gamma = self._cea.get_IvacCstrTc_ChmMwGam(
            **kwargs
        )
        isp_sl, _ = self._cea.estimate_Ambient_Isp(**kwargs)

        # 3. Convert English -> SI
        return ChamberProperties(
            gamma=float(gamma),
            molecular_weight_kg_per_kmol=float(mw),
            chamber_temperature_k=float(tc) * _RANKINE_TO_KELVIN,
            cstar_m_s=float(cstar) * _FT_S_TO_M_S,
            isp_vac_s=float(isp_vac),
            isp_sea_level_s=float(isp_sl),
        )

    def get_performance_at_exit(
        self,
        chamber_pressure_pa: float,
        expansion_ratio: float,
    ) -> tuple[float, float, float]:
        """Return (exit_mach, exit_pressure_pa, exit_temperature_k).

        All inputs are SI. Exit pressure is returned in Pa.
        """
        # 1. Convert SI -> English
        pc_psia = chamber_pressure_pa * _PA_TO_PSIA

        # 2. Call RocketCEA
        kwargs = self._build_kwargs(pc_psia, expansion_ratio)
        mach = self._cea.get_MachNumber(**kwargs)

        # 3. Compute exit pressure from isentropic relation (English)
        gamma = self.get_chamber_properties(chamber_pressure_pa, expansion_ratio).gamma
        p_exit_psia = pc_psia * (
            1.0 + (gamma - 1.0) / 2.0 * mach**2.0
        ) ** (-gamma / (gamma - 1.0))

        # 4. Convert English -> SI
        p_exit_pa = p_exit_psia * _PSIA_TO_PA

        return float(mach), p_exit_pa, 0.0
