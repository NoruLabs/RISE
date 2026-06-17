# Changelog

All notable changes to RISE are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.2.0] — Stage 21
### Added
- `RunParametricStudy` use case: sweeps a single parameter across N values
- `POST /parametric` API endpoint
- Parametric Study tab in the dashboard
- `ParametricResult` DTO holding all individual `SimulationResult` objects

## [1.1.0] — Stage 20
### Added
- `combustion_efficiency` field in `SimulationInput` and API schema (default 1.0)
- `nozzle_efficiency` field in `SimulationInput` and API schema (default 1.0)
- `AltitudeService` with US Standard Atmosphere 1976 pressure model
- `altitude_sweep_m` optional field in engine config and API schema
- `AltitudePoint` in `SimulationResult` — thrust and Isp at each requested altitude
- Altitude sweep tab in dashboard

## [1.0.0] — Stages 1–16
### Added
- Full clean-architecture RISE core: domain, application, infrastructure, interfaces
- CLI runner with YAML config loading
- RocketCEA thermochemistry adapter
- Geometry service (throat, chamber, nozzle dimensions)
- Transient simulation (Euler integration)
- Plotly chart output
- Validation framework
- FastAPI backend (Stage 17)
- Web UI dashboard (Stage 18)
- Nozzle SVG diagram and isentropic flow profiles (Stage 19)
