# Sample Data

This directory contains sample OpenMC depletion results files for testing and demonstration purposes.

## Data Description

The sample data represents a PWR pin cell depletion calculation with the following characteristics:
- Fuel pin with radius 0.39218 cm
- Power density of 174 W/cm³
- 4 time steps of 30 days each
- 10,000 particles per batch, 100 batches total

## Generation

This sample data was obtained with the following OpenMC depletion calculation:

```python
from contextlib import chdir
from pathlib import Path
from math import pi

import openmc
import openmc.deplete
from openmc.examples import pwr_pin_cell

# Official OpenMC ENDF-B/VIII.0 cross-sections
openmc.config["cross_sections"] = Path("/endfb8/cross_sections.xml")

# Official OpenMC simplified thermal chain
openmc.config["chain_file"] = Path("./chain_casl_pwr.xml")

with chdir("results"):
    model = pwr_pin_cell()
    model.materials[0].volume = pi * (0.39218 ** 2)

    model.settings.particles = 10000
    model.settings.inactive = 10
    model.settings.batches = 100

    operator = openmc.deplete.CoupledOperator(model)

    power = 174
    time_steps = [30] * 4

    integrator = openmc.deplete.PredictorIntegrator(
        operator, time_steps, power, timestep_units='d'
    )

    integrator.integrate()
```