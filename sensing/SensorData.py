from __future__ import annotations

from compatibility.AirSim import airsim, available as ASAVAILABLE
from compatibility.Typing import Union
from drone.BatteryData import BatteryData
from utils import Conversion
from utils.Data import Data
from utils.math.Coordinates import Coordinates
from utils.math.Vector import Vector3


class SensorData(Data):
    TYPES: dict[str, type] = {**Data.TYPES,
            "sensor"   : str,
            "timestamp": float
            }
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """
    
    SENSOR_SPECIFIC = {
            "GPS"             : {
                    "coords": Coordinates,
                    "alt"   : float,
                    "hDil"  : float,
                    "vDil"  : float,
                    "hAcc"  : float,
                    "vAcc"  : float
                    },
            "Velocity"        : {
                    "vel": Vector3
                    },
            "Battery"         : {
                    "battery": BatteryData
                    },
            "AirSim"          : {
                    "position"          : airsim.Vector3r if ASAVAILABLE else None,
                    "angularVelocity"   : airsim.Vector3r if ASAVAILABLE else None,
                    "linearAcceleration": airsim.Vector3r if ASAVAILABLE else None,
                    "linearVelocity"    : airsim.Vector3r if ASAVAILABLE else None,
                    "orientation"       : airsim.Quaternionr if ASAVAILABLE else None
                    },
            }
    
    def __init__(self, dataDict: Union[dict, bytes], timestamp: float = None, sensor: str = None):
        if isinstance(dataDict, bytes):
            sensorInd: int = dataDict[0]
            tl: int = dataDict[1] + 2
            timestamp: bytes = Conversion.fromBytes(dataDict[2: tl], float)
            dataDict: dict = Conversion.dataDictFromBytes(self.SENSOR_SPECIFIC[sorted(self.SENSOR_SPECIFIC)[sensorInd]],
                                                          dataDict[tl:])
            dataDict["timestamp"] = timestamp
        elif isinstance(dataDict, dict):
            tN: bool = timestamp is not None
            sN: bool = sensor is not None
            if tN or "timestamp" not in dataDict:
                dataDict["timestamp"] = timestamp if tN else 0.
            if sN or "sensor" not in dataDict:
                dataDict["sensor"] = sensor if sN else ""
        super().__init__(dataDict)
    
    @staticmethod
    def fromJson(jsonString: str) -> SensorData:
        dataDict: dict = SensorData._jsonDict(SensorData.TYPES, jsonString)
        return SensorData(dataDict, dataDict["timestamp"], dataDict["sensor"])
    
    def __bytes__(self):
        sensor: bytes = bytes([sorted(self.SENSOR_SPECIFIC).index(self.sensor)])
        sensor = Conversion.toBytes(len(sensor)) + sensor
        timestamp: bytes = Conversion.toBytes(self.timestamp)
        timestamp = bytes([len(timestamp)]) + timestamp
        ints: list[int] = []
        for i, (k, v) in enumerate(sorted({k: v for k, v in self.SENSOR_SPECIFIC[self.sensor].items()})):
            # Format: [key, length of value bytes, bytes]
            b: bytes = Conversion.toBytes(v)
            ints += bytes([i, len(b)]) + b
        return sensor + timestamp + bytes(ints) + Conversion.toBytes(
                {k: v for k, v in self._data.items()
                 if k not in self.SENSOR_SPECIFIC[self.sensor] or k not in self.TYPES})
    
    def _check(self):
        return self.SENSOR_SPECIFIC[self.sensor].keys() <= self._data.keys() \
               and all(type(self[key]) is self.SENSOR_SPECIFIC[self.sensor][key]
                       for key in self.SENSOR_SPECIFIC[self.sensor])
    
    @property
    def sensor(self) -> str:
        return self["sensor"]
    
    @property
    def timestamp(self) -> float:
        return self["timestamp"]
