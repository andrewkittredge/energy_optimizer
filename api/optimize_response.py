from pydantic import BaseModel


class OptimizeResponse(BaseModel):
    solar_capacity: float
    battery_capacity: float
    off_peak_grid_usage: float
    peak_grid_consumption: float