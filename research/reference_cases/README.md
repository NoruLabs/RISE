# Reference Cases

This folder contains known-good benchmark cases for validating the RISE simulation.

Each reference case stores expected values from a trusted source (NASA CEA, JANNAF, or published test data).

## Format

Cases are stored as JSON with:
- `name`: Case identifier
- `source`: Origin of the reference data
- `propellants`: Oxidizer and fuel names
- `operating_conditions`: Pressure, expansion ratio, etc.
- `expected_values`: Reference values for validation
- `tolerance`: Acceptable percent error for each metric

## Usage

Validation is run as a post-processing step. The simulation produces values, then the validator compares them against the reference case and reports error.
