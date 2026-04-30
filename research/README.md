# Study Map

The focus is on understanding enough propulsion, math, and software design.

1. Rocket propulsion basics — thrust, mass flow, specific impulse, and why rockets work.
2. Nozzle flow and area ratio — choking, expansion, exit Mach number, and altitude effects.
3. Thermochemistry and propellants — chamber temperature, mixture ratio, and ideal performance.
4. Internal ballistics or feed-system behavior — depending on whether the simulator targets solids or liquids.
5. Numerical simulation basics — state variables, time stepping, and validation against references.
6. Software architecture for engineering tools — modular code, tests, and reproducible inputs/outputs.

## What each area gives the project

### Rocket propulsion basics
This provides the minimum language of the simulator: thrust, exhaust velocity, mass flow, and efficiency. NASA’s introductory propulsion material explains that rocket thrust comes from accelerating exhaust and that rockets carry their own working fluid, which is why they work in space.

### Nozzle flow and area ratio
This explains why the throat and exit geometry matter. NASA’s area-ratio material shows that the throat sets the choked condition and the area ratio controls the expansion to exit conditions, which directly shapes performance.

### Thermochemistry and propellants
This connects propellant choice to chamber temperature, specific impulse, and optimal mixture behavior. RocketCEA wraps NASA CEA specifically to compute quantities such as Isp, Cstar, and chamber temperature from propellant definitions and operating conditions.

### Internal ballistics or liquid feed behavior
This decides how the engine changes over time. Solid-motor path clearly: chamber pressure and thrust are estimated from propellant properties, grain geometry, and nozzle specifications, with geometry regression handled numerically.

### Numerical simulation basics
This teaches how to evolve an engine state over time instead of calculating only one operating point. That includes defining states, updating them every time step, and checking whether the trends make physical sense.

https://www.grc.nasa.gov/www/k-12/rocket/astar.html
https://www.grc.nasa.gov/www/k-12/airplane/Images/specimp.gif
https://rocketcea.readthedocs.io/en/latest/