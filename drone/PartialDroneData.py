from __future__ import annotations

from compatibility.Copy import deepcopy
from compatibility.Typing import Any, Optional, ItemsView, Union
from drone.BatteryData import BatteryData
from drone.DroneState import DroneState
from utils import Conversion
from utils.ConfigurationData import ConfigurationData
from utils.Data import Data
from utils.math.Coordinates import Coordinates
from utils.math.Vector import Vector3


class PartialDroneData(Data):
    TYPES: dict[str, type] = {**Data.TYPES,
            "id"              : int,
            "descriptor"      : str,
            "currentTarget"     : Vector3,
            "position"        : Vector3,  # Relative to start [Δlat, Δlng, Δalt] in m
            "coordinates"     : Coordinates,  # The coordinates of the drone
            "rotation"        : Vector3,  # Euler angles in degrees, [roll, pitch, yaw]
            "acceleration"    : Vector3,  # Acceleration in m/s^2 , [forward, right, down]
            "velocity"        : Vector3,  # Velocity in m/s , [north, east, down]
            "angularVelocity" : Vector3,
            # Angular velocity in rad/s , [forward, right, down] # I don't know what "forward" angular velocity means, see MAVSDK
            "startingPosition": Coordinates,  # Starting coordinates
            "battery"         : BatteryData,
            "startTime"       : float,
            "state"           : str,
            "flockGroup"      : int,
            "neighbours"       : dict
            }
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """

    __DEFAULTS: dict[str, Any] = {
                "id": -1,
                "descriptor": "",
                "currentTarget": Vector3(),
                "position"        : Vector3(),
                "coordinates"     : Coordinates(0, 0),
                "rotation"        : Vector3(),
                "acceleration"    : Vector3(),
                "velocity"        : Vector3(),
                "angularVelocity" : Vector3(),
                "startingPosition": Coordinates(0.0, 0.0),
                "battery"         : BatteryData({}, 0, 0.0, 0.0),
                "startTime"       : 0.0,
                "state"           : DroneState.INITIALIZATION.name,
                "flockGroup"      : 0,
                "neighbours"      : {}
                }

    @staticmethod
    def DEFAULTS(configData: ConfigurationData = None) -> dict[str, Any]:
        if configData:
            PartialDroneData.__DEFAULTS.update({"id"              : configData.drone["id"],
                                                "descriptor"      : configData.drone["descriptor"]})
        return deepcopy(PartialDroneData.__DEFAULTS)
    
    def __init__(self, dataDict: Union[bytes, dict[Any, Any]] = {}, *args, **kwargs):
        if isinstance(dataDict, bytes):
            dataDict = Conversion.dataDictFromBytes(self.TYPES, dataDict)
        if "state" in dataDict and isinstance(dataDict["state"], DroneState):
            dataDict["state"] = dataDict["state"].name
        self.__unused: set[str] = set(self.TYPES.keys()) - set(dataDict.keys())
        for key in self.__unused:
            dataDict[key] = deepcopy(self.DEFAULTS()[key])
        super().__init__(dataDict)
    
    @staticmethod
    def fromJson(jsonString: str) -> PartialDroneData:
        return PartialDroneData(PartialDroneData._jsonDict(PartialDroneData.TYPES, jsonString))
    
    def toJson(self) -> dict:
        return {k: v for k, v in self.items if k not in self.__unused}
    
    def __bytes__(self) -> bytes:
        # Format: len(bytes) + bytes(in TYPES) + len(rest) + bytes(not in TYPES)
        bytelist: bytes = bytes()
        for i, (k, v) in enumerate(sorted(self._data.items())):
            # Format: [key (1 byte), length of value bytes, bytes]
            if k in self.__unused:
                continue
            b: bytes = Conversion.toBytes(v)
            bytelist += bytes([i, len(b)]) + b
        return bytes([len(bytelist)]) + bytelist + Conversion.toBytes({k: v for k, v in self._data.items()
                                                                       if k not in self.TYPES})
    
    def __repr__(self) -> str:
        return str({k: str(v) for k, v in self.items if k not in self.__unused})
    
    def __contains__(self, item: str) -> bool:
        return item not in self.__unused and super().__contains__(item)
    
    def __getitem__(self, item: str) -> Optional[Any]:
        return None if item in self.__unused else super().__getitem__(item)
    
    def __setitem__(self, key: str, value: Any):
        if key not in self.__unused:
            super().__setitem__(key, value)
    
    @property
    def items(self) -> ItemsView[Any, Any]:
        return {k: v for k, v in super().items if k not in self.__unused}.items()
