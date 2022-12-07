from __future__ import annotations

from compatibility.Copy import deepcopy
from compatibility.Typing import Any, Union
from drone.BatteryData import BatteryData
from drone.DroneState import DroneState
from drone.PartialDroneData import PartialDroneData
from utils.Data import Data
from utils.math.Coordinates import Coordinates
from utils.math.Vector import Vector3


class DroneData(PartialDroneData):
    
    def __init__(self, dataDict: Union[bytes, dict[Any, Any]]):
        super().__init__(dataDict)
    
    @staticmethod
    def fromJson(jsonString: str) -> DroneData:
        return DroneData(DroneData._jsonDict(DroneData.TYPES, jsonString))
    
    def update(self, partial: Data):
        for key in self.TYPES:
            if key in partial:
                if key == "coordinates":
                    partial["position"] = partial[key].calcPositionalVector(self["startingPosition"])
                self[key] = deepcopy(partial[key])
    
    @property
    def position(self) -> Vector3:
        return self["position"]
    
    @property
    def coordinates(self) -> Vector3:
        return self["coordinates"]
    
    @property
    def rotation(self) -> Vector3:
        return self["rotation"]
    
    @property
    def acceleration(self) -> Vector3:
        return self["acceleration"]
    
    @property
    def velocity(self) -> Vector3:
        return self["velocity"]
    
    @property
    def angularVelocity(self) -> Vector3:
        return self["angularVelocity"]
    
    @property
    def startingPosition(self) -> Coordinates:
        return self["startingPosition"]
    
    @property
    def battery(self) -> BatteryData:
        return self["battery"]
    
    @property
    def startTime(self) -> int:
        return self["startTime"]
    
    @property
    def state(self) -> DroneState:
        return DroneState[self["state"]]
    
    @property
    def flockGroup(self) -> int:
        return self["flockGroup"]
    
    @property
    def neighbours(self) -> dict:
        return self["neighbours"]
