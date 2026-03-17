"""
Ride class for Green ny-text trips,
with serializer and deserializer.
"""

import dataclasses
from dataclasses import dataclass
import json
from typing import Self

import pandas as pd


@dataclass
class Ride:
    """
    Usefull columns for green taxi dataset
    """

    lpep_pickup_datetime: str
    lpep_dropoff_datetime: str
    PU_location_id: int
    DO_location_id: int
    passenger_count: int | None  # this feature has some NaN values
    trip_distance: float
    tip_amount: float
    total_amount: float

    @classmethod
    def from_row(cls, row: pd.Series) -> Self:
        """
        Return a Ride object from a Pandas Series row.
        """
        passenger_count_value = row["passenger_count"]
        return cls(
            lpep_pickup_datetime=str(row["lpep_pickup_datetime"]),
            lpep_dropoff_datetime=str(row["lpep_dropoff_datetime"]),
            PU_location_id=int(row["PULocationID"]),
            DO_location_id=int(row["DOLocationID"]),
            passenger_count=int(passenger_count_value)
            if pd.notna(passenger_count_value)
            else None,
            trip_distance=float(row["trip_distance"]),
            tip_amount=float(row["tip_amount"]),
            total_amount=float(row["total_amount"]),
        )

    @classmethod
    def deserializer(cls, data: bytes) -> Self:
        json_str = data.decode("utf-8")
        ride_dict = json.loads(json_str)
        return cls(**ride_dict)

    def serializer(self) -> bytes:
        ride_dict = dataclasses.asdict(self)
        json_str = json.dumps(ride_dict)
        return json_str.encode("utf-8")
