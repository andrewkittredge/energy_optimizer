# Copilot / AI Agent Instructions for energy_optimizer

This repository is a small Pyomo-based energy optimization prototype implemented as a Jupyter notebook (`power.ipynb`) and a minimal `Dockerfile` that uses the `gurobi/python:13.0.0_3.13` base image.

Key points for an AI coding agent working here:

- **Big picture:** The code models a household energy cost optimization (solar sizing, battery sizing, off-peak/peak usage) using Pyomo (including GDP/disjunctions). The main model and examples live in `power.ipynb`.
- **Runtime / solver:** The project expects Gurobi via the base Docker image. `power.ipynb` calls `pyo.SolverFactory("gurobi")`. A valid Gurobi license is required when using that solver. If a contributor can't use Gurobi, suggest/how-to switch to an open solver (install and change `SolverFactory("gurobi")` -> `SolverFactory("cbc")` or similar) and document limitations.
- **Dependencies & build:** `Dockerfile` installs `pyomo`, `notebook`, `black`, and `pint` with pip. The base image includes Gurobi. Useful commands:

  - Build: `docker build -t energy_optimizer .`
  - Run notebook inside container: `docker run --rm -it -p 8888:8888 energy_optimizer jupyter notebook --ip=0.0.0.0 --no-browser --allow-root`
  - If working locally without Docker: `pip install pyomo notebook black pint` (note: Gurobi still required for the default solver call).

- **Project-specific patterns (copy examples into code edits when relevant):**

  - Solar sizes: `SOLAR_INSTALLATION_SIZES` is a dict mapping kW -> levelized cost. Code chooses sizes via binary flags and an SOS1 constraint:

    - `model.SOLAR_SIZES = pyo.Set(initialize=SOLAR_INSTALLATION_SIZES.keys())`
    - `model.solar_size_flags = pyo.Var(model.SOLAR_SIZES, within=pyo.Binary)`
    - `model.sos1_constraint = pyo.SOSConstraint(var=model.solar_size_flags, sos=1)`

  - Costs & units: the notebook uses `pint` units through `pyomo.util.check_units` and `units.load_definitions_from_strings`. Calls to `assert_units_consistent(...)` are present and should be preserved when refactoring.

  - GDP/disjunctions: the battery sizing uses `pyomo.gdp` Disjuncts + `TransformationFactory('gdp.bigm')`. When editing constraints that participate in the disjunction, keep the same transformation approach unless you fully replace it and update tests/examples.

- **Conventions & small gotchas:**

  - The repo is notebook-first. When proposing code changes, include a small runnable Python snippet or a notebook cell example that demonstrates the change (not only a library function). Reference `power.ipynb` cell structure when adding examples.
  - Keep unit checks (`assert_units_consistent`) in place; they document implicit assumptions and often catch errors.
  - Formatting: `black` is included in the Docker image. Use `black .` for Python files (notebooks should be left as-is unless converting to .py).

- **When to ask the user:**

  - If a change affects solver selection, ask whether to assume Gurobi (requires license) or to switch to/experiment with an open-source solver.
  - If you need to add new dependencies, ask whether to update the `Dockerfile` or add a `requirements.txt` so CI / contributors can reproduce builds.

Reference files to inspect for more context: `power.ipynb`, `Dockerfile`.

If you want, I can (a) convert `power.ipynb` to a small runnable `scripts/` module and add a `requirements.txt`, or (b) add a short `README.md` documenting the run/build steps — tell me which you'd prefer.
