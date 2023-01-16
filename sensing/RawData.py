from __future__ import annotations

from compatibility.Typing import Union
from utils.Data import Data


class RawData(Data):
    TYPES: dict[str, type] = {**Data.TYPES,
                              "source": str
                              }
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """
    
    def __init__(self, dataDict: Union[bytes, dict], source: str = None):
        if isinstance(dataDict, dict):
            sN: bool = source is not None
            if sN or "source" not in dataDict:
                dataDict["source"] = source if sN else ""
        super().__init__(dataDict)
    
    @staticmethod
    def fromJson(jsonString: str) -> RawData:
        dataDict: dict = RawData._jsonDict(RawData.TYPES, jsonString)
        return RawData(dataDict, dataDict["source"])
    
    @property
    def source(self) -> str:
        return self["source"]
