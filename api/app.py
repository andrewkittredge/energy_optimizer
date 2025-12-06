from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/optimize")
def optimize(body: Dict[str, Any] | None = None):
    """Accept JSON body with optional params and run the optimizer.

    Supported keys (same as script `build_model(params=...)`):
      - peak_price, off_peak_price, battery_cost_per_kw
      - peak_consumption, off_peak_consumption
      - solar_installation_sizes (map of size->cost)
    """
    body = body or {}

    # Convert solar size keys to ints when provided as strings
    if "solar_installation_sizes" in body:
        sizes = body["solar_installation_sizes"]
        try:
            sizes = {int(k): float(v) for k, v in sizes.items()}
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail="Invalid solar_installation_sizes format"
            )
        body["solar_installation_sizes"] = sizes

    model = run_optimizer.build_model(params=body)

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
