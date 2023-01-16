from __future__ import annotations  # Use "CommandData" in type annotations

from compatibility.Typing import Any, Union  # Type annotations
from communication.Command import Command  # Command class for "cmd" element
from utils import Conversion
from utils.Data import Data  # Data class for "msg" element


class CommandData(Data):
    """ Class for storing command data: command-type and message (arguments) """
    
    TYPES: dict[str, type] = {**Data.TYPES,
            "cmd": str,  # Command type
            "msg": Data  # Message (arguments)
            }
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """
    
    def __init__(self, dataDict: Union[bytes, dict[Any, Any]] = None, cmd: Command = None,
                 msg: Union[Data, dict] = None, *args, **kwargs):
        """
        Initialize CommandData instance with explicit data or encoded data (bytes)
        
        :param dataDict: dataDict to initialize instance with
        :param cmd: command type (Not required if given in dataDict)
        :param msg: message (arguments) (Not required if given in dataDict)
        """
        if dataDict is None:
            dataDict: dict[Any, Any] = {}
        if isinstance(dataDict, bytes):  # Convert bytes to dict if data given as bytes (encoded)
            dataDict = Conversion.dataDictFromBytes(self.TYPES, dataDict)
        elif isinstance(dataDict, dict):  # Fill dataDict with given arguments or override old values
            cN: bool = cmd is not None
            mN: bool = msg is not None
            if cN or "cmd" not in dataDict:  # If cmd is given or not in dataDict
                dataDict["cmd"] = (cmd if isinstance(cmd, str) else cmd.name) if cN else ""
            if mN or "msg" not in dataDict:  # If msg is given or not in dataDict
                dataDict["msg"] = (Data(msg) if isinstance(msg, dict) else msg) if mN else Data({})
        super().__init__(dataDict)  # finish initialization with dataDict and check validity using TYPES
    
    @staticmethod
    def fromJson(jsonString: str) -> CommandData:
        """
        Create CommandData instance from JSON string
        
        :param jsonString: JSON string to create instance from
        :return: CommandData instance created from JSON string
        
        .. seealso:: :meth:`utils.Data.Data._jsonDict`
        """
        dataDict: dict = CommandData._jsonDict(CommandData.TYPES, jsonString)  # Get dataDict from JSON
        return CommandData(dataDict)  # Create CommandData instance from dataDict
    
    @property
    def cmd(self) -> Command:
        """
        Get command-type of CommandData instance
        
        :return: command-type of CommandData instance
        """
        return Command[self["cmd"]]
    
    @property
    def msg(self) -> Any:
        """
        Get message (arguments) of CommandData instance
        
        :return: message (arguments) of CommandData instance
        """
        return self["msg"]
