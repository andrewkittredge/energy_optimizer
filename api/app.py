from __future__ import annotations

from fastapi import FastAPI, HTTPException
from starlette.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware


from .optimize_response import OptimizeResponse
from .optimize_params import OptimizeParams
import api.run_optimizer as run_optimizer

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Energy Optimizer API")


# Allow local demo UI to talk to this API. Tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/defaults")
def get_defaults() -> OptimizeParams:
    """Return the default optimization parameters."""
    return OptimizeParams()


@app.post("/optimize")
def optimize(params: OptimizeParams | None = None) -> OptimizeResponse:
    """Accept JSON body with optional params and run the optimizer.

    Supported keys (same as script `build_model(params=...)`):
      - peak_price, off_peak_price, battery_cost_per_kw
      - peak_consumption, off_peak_consumption
      - solar_installation_sizes (map of size->cost)
    """

    model = run_optimizer.build_model(params=params)

    try:
        run_optimizer.solve_model(model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"solver error: {exc}")
    return OptimizeResponse(
        solar_capacity=float(model.solar_capacity.value),
        battery_capacity=float(model.battery_capacity.value),
        off_peak_grid_usage=float(model.off_peak_grid_usage.value),
        peak_grid_consumption=float(model.peak_grid_consumption.value),
    )


# Path to Angular build output
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "app",
    "dist",
    "energy-optimizer",
    "browser",
)
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


mcp = FastMCP.from_fastapi(app=app, stateless_http=True)


@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"


starlette_app = mcp.http_app()

starlette_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":

    # Run the server
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)
