# Changelog

## [1.0.0] - 2026-06-13

### Added
- Domain models: Engine, Nozzle, OperatingPoint
- Thrust and specific impulse calculation
- Nozzle geometry: throat, chamber, exit diameter, L*, bell nozzle
- 0D chamber pressure transient simulation
- RocketCEA integration for thermochemistry (LOX/LH2 and others)
- YAML engine config with Pydantic schema validation
- Plotly plotting: chamber pressure, thrust, mass flow (PNG + HTML)
- Validation against reference data with error metrics
- CLI entry point: `rise --config <file>`
- GitHub Actions CI: ruff, mypy, pytest on every push
- 99% test coverage
