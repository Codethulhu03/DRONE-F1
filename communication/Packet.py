from __future__ import annotations  # for "Packet" type hints

from compatibility.Typing import Any, Union  # for type hints in __init__

import utils.Conversion as Conversion  # for converting to and from bytes
from utils.Data import Data  # Base class for "Data" structures
import communication.TypeHashDict as THD  # for converting data type to index

class Packet(Data):
    """ Class for communication packets """
    
    TYPES: dict[str, type] = {**Data.TYPES,
            "commChannel"  : str,
            "commInterface": str,
            "payload"      : Data,
            "type"         : int
            }
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """
    
    def __init__(self, payload: Union[dict[str, Any], bytes], commInterface: str = "",
                 commChannel: str = "", *args, **kwargs):
        """
        Initialize a new Packet instance
        
        :param payload: payload of the packet
        :param commInterface: communication interface of the packet (not required if given in payload)
        :param commChannel: communication channel of the packet (not required if given in payload)
        """
        data: dict[str, Any] = {}
        if isinstance(payload, (bytes, bytearray)):  # set __bytes if data given as bytes instance
            self.__bytes: bytes = payload
            try:
                types = Packet.TYPES.copy()
                types["payload"] = THD.DATA_TYPES[Packet._jsonDict({"type": int}, payload)["type"]]
                fromjson: dict[str, Any] = Packet._jsonDict(types, payload)
                data["payload"] = fromjson["payload"]
                commChannel = fromjson["commChannel"]
            except Exception as e:
                data = {"payload": Data({}), "type": -1}
        else:
            self.__bytes: bytes = None
            if not isinstance(payload, Data):
                payload = Data(payload)
            data["payload"] = payload
        if commChannel or "commChannel" not in data:
            data["commChannel"] = commChannel
        else:
            data["commChannel"] = data["commChannel"].name
        if commInterface or "commInterface" not in data:
            data["commInterface"] = commInterface
        if "type" not in data:
            data["type"] = THD.DATA_TYPES.index(type(data["payload"]))
        super().__init__(data)  # finish initialization with dataDict and check validity using TYPES

    @staticmethod
    def fromJson(jsonString: str) -> Packet:
        """
        Create a new Packet instance from a JSON string
        
        :param jsonString: JSON string to create the Packet from
        :return: new Packet instance
        
        .. seealso:: :meth:`utils.Data.Data._jsonDict`
        """
        dataDict: dict = Packet._jsonDict(Packet.TYPES, jsonString)
        return Packet(dataDict, dataDict["commInterface"],
                      dataDict["commChannel"])
    
    @property
    def bytes(self) -> bytes:
        """
        Get the bytes representation of the packet
        
        :return: bytes representation of the packet
        """
        if self.__bytes is None:
            cI: str = self.commInterface
            del self._data["commInterface"]  # Don't send communication interface name
            self.__bytes = Conversion.jsonDumps(self)
            self.commInterface = cI   # Restore communication interface name
        return self.__bytes
    
    @bytes.setter
    def bytes(self, value: bytes):
        """
        Set the bytes representation of the packet
        
        :param value: bytes representation of the packet
        """
        self.__bytes = value
    
    @property
    def commInterface(self) -> str:
        """
        Get the communication interface of the packet
        
        :return: communication interface name
        """
        return self["commInterface"]

    @property
    def type(self) -> int:
        """
        Get the data type index of the payload

        :return: data type index (see TypeHashDict.DATA_TYPES)
        """
        return self["type"]
    
    @commInterface.setter
    def commInterface(self, value: str):
        """
        Set the communication interface of the packet
        
        :param value: communication interface name
        :return:
        """
        self._data["commInterface"] = value
    
    @property
    def payload(self) -> Data:
        """
        Get the payload of the packet
        
        :return: payload of the packet
        """
        return self["payload"]
    
    @property
    def commChannel(self) -> str:
        """
        Get the communication channel of the packet
        
        :return: communication channel name
        """
        return self["commChannel"]
    
    @commChannel.setter
    def commChannel(self, value: str):
        """
        Set the communication channel of the packet
        
        :param value: communication channel name
        """
        self._data["commChannel"] = value
