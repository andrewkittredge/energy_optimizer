from typing import Dict, Optional
from pydantic import BaseModel


class OptimizeParams(BaseModel):
    peak_price: float = 0.5
    off_peak_price: float = 0.4
    battery_cost_per_kw: float = 0.15
    peak_consumption: float = 10
    off_peak_consumption: float = 20
    # Accept JSON string keys (typical when sent from JS). We'll coerce to int below.
    solar_installation_sizes: Dict[float, float] = {
        3: 0.282,
        5: 0.250,
        6: 0.230,
        8: 0.210,
        10: 0.190,
        12: 0.117,
    }

