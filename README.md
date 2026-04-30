# RISE

RISE is the Rocket Integrated Simulation Environment. It is a small Python
package for modeling rocket engine operating points and computing basic
performance values such as expansion ratio, thrust, and specific impulse.

## Install

Create a virtual environment, then install the package with its development
tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run

After installation, run the console command:

```powershell
rise
```

You can also run the module directly:

```powershell
python -m rise.main
```

## Test

Run the test suite with:

```powershell
pytest
```
