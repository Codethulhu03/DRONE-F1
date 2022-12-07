from __future__ import annotations

from compatibility.Typing import Any
from utils.Data import Data


class BatteryData(Data):
    TYPES = dict(Data.TYPES, **{
            "level"  : int,
            "voltage": float,
            "current": float
            })
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """
    
    def __init__(self, dataDict: dict[Any, Any] = None, level: int = None, voltage: float = None, current: float = None,
                 *args, **kwargs):
        if dataDict is None:
            dataDict: dict[Any, Any] = {}
        if isinstance(dataDict, dict):
            lN: bool = level is not None
            vN: bool = voltage is not None
            cN: bool = current is not None
            if lN or "level" not in dataDict:
                dataDict["level"] = level if lN else 0
            if vN or "voltage" not in dataDict:
                dataDict["voltage"] = voltage if vN else 0.
            if cN or "current" not in dataDict:
                dataDict["current"] = current if cN else -1.
        super().__init__(dataDict)
    
    @staticmethod
    def fromJson(jsonString: str) -> BatteryData:
        dataDict = BatteryData._jsonDict(BatteryData.TYPES, jsonString)
        return BatteryData(dataDict)
    
    @property
    def current(self) -> float:
        return self["current"]
    
    @property
    def voltage(self) -> float:
        return self["voltage"]
    
    @property
    def level(self) -> int:
        return self["level"]
