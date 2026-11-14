"""Unit conversion and physical validation utilities for EarthScope."""

from typing import Union
import numpy as np
import pandas as pd


def kelvin_to_celsius(k: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
    """Convert absolute temperature in Kelvin to degrees Celsius.
    Formula: °C = K - 273.15
    """
    return k - 273.15


def celsius_to_kelvin(c: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
    """Convert degrees Celsius to Kelvin.
    Formula: K = °C + 273.15
    """
    return c + 273.15


def flux_to_mm_per_day(flux_kg_m2_s: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
    """Convert water flux in kg m-2 s-1 to equivalent rate in mm/day.
    1 kg/m^2 of water = 1 mm depth (assuming water density 1000 kg/m^3).
    1 day = 86,400 seconds.
    Rate (mm/day) = flux (kg m-2 s-1) * 86,400 s/day
    """
    return flux_kg_m2_s * 86400.0


def flux_to_monthly_accumulation(
    flux_kg_m2_s: pd.Series, timestamps: pd.Series
) -> pd.Series:
    """Convert continuous monthly flux (kg m-2 s-1) to total accumulation (mm/month),
    accounting for the exact number of days in each calendar month (28, 29, 30, 31).
    """
    days_in_month = timestamps.dt.days_in_month
    return flux_to_mm_per_day(flux_kg_m2_s) * days_in_month


def convert_variable_to_display_unit(
    var_id: str,
    raw_value: pd.Series,
    timestamps: pd.Series
) -> Tuple_Display:
    """Dispatch variable conversion to its canonical display unit.
    Returns: (display_values, display_unit_name)
    """
    if var_id in ("t2m", "ts"):
        return kelvin_to_celsius(raw_value), "°C"
    elif var_id in ("precipitation", "evapotranspiration"):
        # Primary display unit: mm/month for intuitive hydrological accounting
        return flux_to_monthly_accumulation(raw_value, timestamps), "mm/month"
    elif var_id.startswith("soil_moisture"):
        return raw_value, "kg/m²"
    else:
        return raw_value, "raw"


# Type alias helper
from typing import Tuple as Tuple_Display
