import requests
import pandas as pd
from secrets import open_ei_api_key


def get_electricity_price_from_openei(address: str) -> float | None:
    """
    Fetches the electricity price (cents/kWh) from OpenEI Utility Rates API for a given location.
    Args:
        address (str): The address of the location.
    Returns:
        float: The average electricity price in cents/kWh, or None if not found.
    """
    url = "https://api.openei.org/utility_rates"
    params = {
        "version": "latest",
        "format": "json",
        "api_key": open_ei_api_key,
        "address": "419 putnam ave, Cambridge, MA 02139",
        "detail": "full",
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()["items"]
    df = pd.DataFrame(data)
    df["startdate"] = pd.to_datetime(df["startdate"], unit="s")
    df = df.sort_values("startdate", ascending=False)
    df = df[df["sector"] == "Residential"]
    df = df[df["servicetype"] == "Delivery with Standard Offer"]
    df = df[df["startdate"] == df["startdate"].max()]
    rate = df["energyratestructure"].iloc[0][0][0]
    return rate["rate"] + rate["adj"]
