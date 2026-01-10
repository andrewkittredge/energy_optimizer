from __future__ import annotations

from fastapi import FastAPI, HTTPException

import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from .optimize_response import OptimizeResponse
from .optimize_params import OptimizeParams
import api.run_optimizer as run_optimizer

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import uvicorn

fast_mcp = FastMCP(
    name="Energy Optimizer MCP Server",
    stateless_http=True,
    instructions="""
This server helps you decide if you should get solar panels and a battery for your home.
Start calling set_address to set your address.
                   """,
    version="0.0.1",
)


@fast_mcp.prompt(
    name="solar prices prompt",
    description="Ask the user about their solar panels price quotes",
)
def ask_solar_prices() -> str:
    return (
        "What price quotes have you received for solar panel installations? "
        "Please provide the size and cost for each quote."
    )


@fast_mcp.tool(name="set_address", description="Set the user's address")
def set_address(address: str) -> str:
    return f"Address set to: {address}"


fast_mcp_app = fast_mcp.http_app(path="/mcp")

fast_api_app = FastAPI(title="Energy Optimizer API", lifespan=fast_mcp_app.lifespan)


fast_api_app.mount("/solar", fast_mcp_app)


@fast_mcp.resource(
    uri="data://defaults",
    description="Default solar optimization parameters",
    name="energy optimizer defaults",
)
@fast_api_app.get("/defaults")
def get_defaults() -> OptimizeParams:
    """Return the default optimization parameters."""
    return OptimizeParams()


@fast_mcp.tool
@fast_api_app.post("/optimize")
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
    fast_api_app.mount(
        "/", StaticFiles(directory=frontend_dist, html=True), name="frontend"
    )
else:
    raise RuntimeError(
        f"Frontend build not found at {frontend_dist}. Please build the Angular app first."
    )

# Allow local demo UI to talk to this API. Tighten in production.
fast_api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    # Run the server
    uvicorn.run(fast_api_app, host="127.0.0.1", port=8000)
