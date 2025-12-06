# energy_optimizer

Small Pyomo-based energy optimization prototype. The original implementation lives in `power.ipynb`; this repository also includes a runnable script version at `scripts/run_optimizer.py`.

Quick start (using the included Dockerfile with Gurobi):

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

Frontend + API (lightweight demo)

- A small static frontend is available in `frontend/index.html` and `frontend/app.js`.
- A lightweight Flask API lives in `api/app.py` and exposes `POST /optimize` which accepts the same parameter keys used by the script (see `scripts/run_optimizer.py` `build_model(params=...)`).

Run the API locally (ensure Python deps installed):

```powershell
pip install -r requirements.txt
python -m api.app
```

Serve the static frontend (from repo root) and use the UI to POST to the API:

```powershell
# serve static files (on port 8000)
python -m http.server 8000 -d frontend
# then open http://localhost:8000 in your browser and click Run optimization
```

Notes:

- The API enables simple parameter overrides (JSON body) — see `api/app.py` for supported keys. The Flask app uses CORS so the demo UI can run from a different port.
- The optimizer still requires a solver. If you run inside the Docker image that uses the Gurobi base, Gurobi will be available. For local testing without Gurobi install and license, install an open-source solver such as `cbc` and run `python -m scripts.run_optimizer --solver cbc` or set the solver programmatically in the API.
