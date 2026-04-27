from dataclasses import dataclass


@dataclass
class Point:
    # Represents one validated GPS point

    time: float
    lat: float
    lon: float
    alt: float

    speed_mps: float = 0.0
    is_anomaly: bool = False
