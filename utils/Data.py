from __future__ import annotations  # Allow "Data" to be used as a type annotation

from compatibility.Typing import Any, ItemsView, Union  # For type annotations
from compatibility.Enum import Enum  # For instance check
from compatibility.Json import loads, dumps  # For JSON serialization

import utils.Conversion as Conversion


class Data:
    TYPES: dict[str, type] = {}
    
    def __init__(self, dataDict: Union[bytes, dict[Any, Any]], *args, **kwargs):
        if isinstance(dataDict, bytes):
            dataDict = Conversion.dataDictFromBytes(self.TYPES, dataDict)
        self._data: dict[Any, Any] = dataDict
        if not self.TYPES.keys() <= self._data.keys():
            raise AttributeError("Not all keys filled")
        for key in self.TYPES:
            t: type = self.TYPES[key]
            if not isinstance(self._data[key], t):
                raise AttributeError(f"Not all types correct: {str(self._data[key])} is not {str(t)}")
        if not self._check():
            raise AttributeError("Check failed")
    
    def toJson(self) -> dict:
        return self._data
    
    def __bytes__(self) -> bytes:
        # Format: len(bytes) + bytes(in TYPES) + len(rest) + bytes(not in TYPES)
        bytelist: bytes = bytes()
        for i, (k, v) in enumerate(sorted(self._data.items())):
            # Format: [key (1 byte), length of value bytes, bytes]
            b: bytes = Conversion.toBytes(v)
            bytelist += bytes([i, len(b)]) + b
        return bytes([len(bytelist)]) + bytelist + Conversion.toBytes({k: v for k, v in self._data.items()
                                                                       if k not in self.TYPES})
    
    @staticmethod
    def fromJson(jsonString: str) -> Data:
        return Data(Data._jsonDict(Data.TYPES, jsonString))
    
    @staticmethod
    def _jsonDict(types: dict, jsonString: str) -> dict:
        if not isinstance(jsonString, dict):
            jsonDict: dict = loads(jsonString)
        else:
            jsonDict: dict = jsonString
        if not isinstance(jsonDict, dict):
            raise AttributeError("json not a dict representation")
        return {k: (types[k].fromJson(dumps(v)) if callable(getattr(types[k], "fromJson", None)) else loads(str(v))
                    if types[k] is dict else types[k](v)) if k in types else v for k, v in jsonDict.items()}
    
    def __contains__(self, item) -> bool:
        return item in self._data
    
    def _check(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        return str({key: str(val) for key, val in self.items})
    
    def __getitem__(self, item: Any):
        if not isinstance(item, (str, Enum)):
            return self[type(item).__name__]
        return self._data[item]

    def __eq__(self, other):
        return str(self) == str(other)

    def __setitem__(self, key: Any, value: Any):
        if key in self._data:
            self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def setdefault(self, key: Any, default: Any) -> Any:
        return self._data.setdefault(key, default)
    
    def get(self, key: Any, default: Any) -> Any:
        return self._data.get(key, default)
    
    @property
    def items(self) -> ItemsView[Any, Any]:
        return self._data.items()
    
    def __eq__(self, other):
        return self._data == other._data

    