from compatibility.Typing import Any
import compatibility.Yaml as yaml
from compatibility.OS import os

from utils.ConfigurationData import ConfigurationData
import communication
import controller
import drone
import sensing

fcsub = [cls for cls in controller.FlightController.__subclasses__() if cls.AVAILABLE]
ccsub = [cls for cls in controller.ChannelController.__subclasses__() if cls.AVAILABLE]
csub = [cls for cls in controller.Controller.__subclasses__()
        if cls.__name__ not in ("FlightController", "ChannelController") and cls.AVAILABLE]
ssub = [cls for cls in sensing.Sensor.__subclasses__() if cls.AVAILABLE]
esub = [cls for cls in sensing.Evaluator.__subclasses__() if cls.AVAILABLE]
commsub = [cls for cls in communication.CommunicationInterface.__subclasses__() if cls.AVAILABLE]
modsub = [cls for cls in drone.Module.__subclasses__()
          if cls.__name__ not in ("CommunicationInterface", "Controller", "Sensor", "Evaluator") and cls.AVAILABLE]


class Configuration:
    AVAILABLE = {
            "flight"       : [cls.__name__ for cls in fcsub],
            "channels"     : [cls.__name__ for cls in ccsub],
            "controllers"  : [cls.__name__ for cls in csub],
            "sensors"      : [cls.__name__ for cls in ssub],
            "evaluators"   : [cls.__name__ for cls in esub],
            "digestions"   : [x.name for x in communication.PacketDigestions],
            "communication": [cls.__name__ for cls in commsub],
            "unknown"      : [cls.__name__ for cls in modsub]
            }
    
    SPEC = {
            "available"    : AVAILABLE,
            "configuration": {k.__name__: k.ARGS for sub in (fcsub, ccsub, csub, ssub, esub, commsub, modsub)
                              for k in sub},
            "drone"        : {"descriptor": "",
                              "id"        : -1,
                              "home"      : "(0.0, 0.0)"},
            "mission"      : "mission.yml",
            "modules"      : {
                    "flight"       : "FlightlessFlightController",
                    "channels"     : [],
                    "controllers"  : [],
                    "sensors"      : [],
                    "evaluators"   : [],
                    "communication": [],
                    "unknown"      : []
                    }
            }
    
    def __init__(self, file: str):
        if not (file.endswith("yaml") or file.endswith("yml")):
            raise ValueError("Configuration must be of type YAML")
        self.__dict: dict[str, Any] = {}
        bad = False
        try:
            self.__dict = yaml.read(file)
        except yaml.yamlError:
            bad = True
        bad |= not self.__dict
        if bad:
            self.__defaults(file)
        self.__dict["available"] = Configuration.AVAILABLE
        yaml.write(self.__dict, file)
        if not self.__check(Configuration.SPEC, self.__dict):
            self.__defaults(file)
        if not self.__available(self.AVAILABLE):
            raise AttributeError("Requested modules not available")
    
    def __defaults(self, file: str):
        os.replace(file, file.replace(".yml", ".backup.yml", 1).replace(".yaml", ".backup.yaml", 1))
        yaml.write(Configuration.SPEC, file)
        raise AttributeError("Configuration file bad, loading defaults")
    
    def __check(self, check: dict[str, Any], spec: dict[str, Any]):
        return (check.keys() == spec.keys()
                and all(isinstance(check[k], type(spec[k])) for k in check)
                and all(self.__check(check[k], spec[k]) for (k, v) in check.items()
                        if isinstance(v, dict)))
    
    def __available(self, available: dict[str, list[str]]):
        return all(self.moduleCollection[k] <= set(available[k]) for k in self.moduleCollection)
    
    @property
    def flight(self) -> str:
        return self.__dict["modules"]["flight"]
    
    @property
    def channels(self) -> list[str]:
        return self.__dict["modules"]["channels"]
    
    @property
    def controllers(self) -> list[str]:
        return self.__dict["modules"]["controllers"]
    
    @property
    def sensors(self) -> list[str]:
        return self.__dict["modules"]["sensors"]
    
    @property
    def evaluators(self) -> list[str]:
        return self.__dict["modules"]["evaluators"]
    
    @property
    def communication(self) -> list[str]:
        return self.__dict["modules"]["communication"]
    
    @property
    def unknown(self) -> list[str]:
        return self.__dict["modules"]["unknown"]
    
    @property
    def moduleCollection(self) -> dict[str, set[str]]:
        return {k: (set(v) if isinstance(v, list) else {v}) for k, v in self.__dict["modules"].items()}
    
    @property
    def data(self) -> ConfigurationData:
        return ConfigurationData({k: v for k, v in self.__dict.items() if k in ConfigurationData.TYPES.keys()})
