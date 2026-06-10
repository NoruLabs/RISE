import os

import plotly.graph_objects as go

from rise.application.dtos.transient_simulation_result import TransientSimulationResult


# Standard filenames for output plots
_CHAMBER_PRESSURE_PNG = "chamber_pressure.png"
_CHAMBER_PRESSURE_HTML = "chamber_pressure.html"
_THRUST_PNG = "thrust.png"
_THRUST_HTML = "thrust.html"
_MASS_FLOW_PNG = "mass_flow.png"
_MASS_FLOW_HTML = "mass_flow.html"


def _build_figure(
    time_s: list[float],
    y_values: list[float],
    y_label: str,
    title: str,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_s,
            y=y_values,
            mode="lines",
            name=title,
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title=y_label,
        template="plotly_white",
    )
    return fig


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _save_both(fig: go.Figure, png_path: str, html_path: str) -> None:
    _ensure_dir(png_path)
    fig.write_image(png_path)
    _ensure_dir(html_path)
    fig.write_html(html_path)


class Plotter:
    """Plotting adapter for transient simulation results.

    Keeps plotting in infrastructure so the application layer
    never depends on Plotly or image formats.
    """

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = output_dir

    def plot_pressure_time(
        self,
        result: TransientSimulationResult,
    ) -> None:
        """Plot chamber pressure vs time and save PNG + HTML."""
        fig = _build_figure(
            result.time_s,
            result.chamber_pressure_pa,
            "Chamber Pressure (Pa)",
            "Chamber Pressure vs Time",
        )
        _save_both(
            fig,
            os.path.join(self.output_dir, _CHAMBER_PRESSURE_PNG),
            os.path.join(self.output_dir, _CHAMBER_PRESSURE_HTML),
        )

    def plot_thrust_time(
        self,
        result: TransientSimulationResult,
    ) -> None:
        """Plot thrust vs time and save PNG + HTML."""
        fig = _build_figure(
            result.time_s,
            result.thrust_n,
            "Thrust (N)",
            "Thrust vs Time",
        )
        _save_both(
            fig,
            os.path.join(self.output_dir, _THRUST_PNG),
            os.path.join(self.output_dir, _THRUST_HTML),
        )

    def plot_mass_flow_time(
        self,
        result: TransientSimulationResult,
    ) -> None:
        """Plot mass flow rate vs time and save PNG + HTML."""
        fig = _build_figure(
            result.time_s,
            result.mass_flow_kg_s,
            "Mass Flow (kg/s)",
            "Mass Flow vs Time",
        )
        _save_both(
            fig,
            os.path.join(self.output_dir, _MASS_FLOW_PNG),
            os.path.join(self.output_dir, _MASS_FLOW_HTML),
        )

    def plot_all(self, result: TransientSimulationResult) -> None:
        """Generate all three plots to the output directory."""
        self.plot_pressure_time(result)
        self.plot_thrust_time(result)
        self.plot_mass_flow_time(result)
