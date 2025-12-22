from __future__ import annotations

from typing import Any, Dict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi_mcp import FastApiMCP

from .optimize_response import OptimizeResponse
from .optimize_params import OptimizeParams
import scripts.run_optimizer as run_optimizer

app = FastAPI(title="Energy Optimizer API")

# Allow local demo UI to talk to this API. Tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files and webpack output
base_path = Path(__file__).parent.parent
frontend_path = base_path / "frontend"
public_path = base_path / "public"

# Mount the webpack output (`public/`) at `/static` so built assets
# produced by webpack are served from /static/*
app.mount("/static", StaticFiles(directory=public_path), name="static")


@app.get("/")
def serve_index() -> FileResponse:
    """Serve the index.html file."""
    return FileResponse(frontend_path / "index.html", media_type="text/html")


@app.post("/optimize")
def optimize(body: OptimizeParams | None = None) -> OptimizeResponse:
    """Accept JSON body with optional params and run the optimizer.

    Supported keys (same as script `build_model(params=...)`):
      - peak_price, off_peak_price, battery_cost_per_kw
      - peak_consumption, off_peak_consumption
      - solar_installation_sizes (map of size->cost)
    """
    params: Dict[str, Any] = {}
    if body is not None:
        params = body.dict(exclude_none=True)

    # Convert solar size keys to ints when provided as strings
    if "solar_installation_sizes" in params:
        sizes = params["solar_installation_sizes"]
        try:
            sizes = {int(k): float(v) for k, v in sizes.items()}
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail="Invalid solar_installation_sizes format"
            )
        params["solar_installation_sizes"] = sizes

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


mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
