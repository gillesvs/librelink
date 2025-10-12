"""Units of measurement for LibreLink integration."""
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class UnitOfMeasurement:
    """Unit of measurement for LibreLink integration."""

    unit_of_measurement: str
    suggested_display_precision: int
    from_mg_per_dl: Callable[[float], float]


UNITS_OF_MEASUREMENT = (
    UnitOfMeasurement(
        unit_of_measurement="mg/dL",
        suggested_display_precision=0,
        from_mg_per_dl=lambda x: x,
    ),
    UnitOfMeasurement(
        unit_of_measurement="mmol/L",
        suggested_display_precision=1,
        from_mg_per_dl=lambda x: x / 18,
    ),
)
