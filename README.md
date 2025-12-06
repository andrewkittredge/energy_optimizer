# energy_optimizer

Small Pyomo-based energy optimization prototype. The original implementation lives in `power.ipynb`; this repository also includes a runnable script version at `scripts/run_optimizer.py`.

Quick start (using the included Dockerfile with Gurobi):

```powershell
docker build -t energy_optimizer .
docker run --rm -it -p 8888:8888 energy_optimizer jupyter notebook --ip=0.0.0.0 --no-browser --allow-root
```

Run the script inside the container or locally (if you have Pyomo & a solver installed):

```powershell
# inside container or with Python deps installed
python -m scripts.run_optimizer --solver gurobi

# if you don't have Gurobi, try an open solver (install solver beforehand):
python -m scripts.run_optimizer --solver cbc
```

Notes:

- The notebook and script use unit checks via `pint`; keep `assert_units_consistent(...)` when refactoring.
- The script preserves the GDP disjunction transformation (`TransformationFactory('gdp.bigm')`).
- Gurobi is not installed via pip; the provided `Dockerfile` uses the `gurobi/python:13.0.0_3.13` base image which includes the solver.
