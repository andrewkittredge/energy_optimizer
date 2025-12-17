from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi_mcp import FastApiMCP

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


class OptimizeParams(BaseModel):
    peak_price: Optional[float] = None
    off_peak_price: Optional[float] = None
    battery_cost_per_kw: Optional[float] = None
    peak_consumption: Optional[float] = None
    off_peak_consumption: Optional[float] = None
    # Accept JSON string keys (typical when sent from JS). We'll coerce to int below.
    solar_installation_sizes: Optional[Dict[str, float]] = None


@app.post("/optimize")
def optimize(body: OptimizeParams | None = None):
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

    summary = {
        "solar_capacity": float(model.solar_capacity.value),
        "battery_capacity": float(model.battery_capacity.value),
        "off_peak_grid_usage": float(model.off_peak_grid_usage.value),
        "peak_grid_consumption": float(model.peak_grid_consumption.value),
    }
    return {"status": "ok", "summary": summary}


mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
