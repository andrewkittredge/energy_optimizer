from typing import Dict, Optional
from pydantic import BaseModel


class OptimizeParams(BaseModel):
    peak_price: Optional[float] = None
    off_peak_price: Optional[float] = None
    battery_cost_per_kw: Optional[float] = None
    peak_consumption: Optional[float] = None
    off_peak_consumption: Optional[float] = None
    # Accept JSON string keys (typical when sent from JS). We'll coerce to int below.
    solar_installation_sizes: Optional[Dict[str, float]] = None

