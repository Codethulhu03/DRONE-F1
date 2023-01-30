from compatibility.Itertools import chain
from compatibility.Functools import cache
from compatibility.Typing import Any, Callable, Iterable
import compatibility.Yaml as yaml
from compatibility.OS import os
from drone import Module

from utils.Subtypes import getSubTypeList
from utils.ConfigurationData import ConfigurationData
import communication
import controller
import drone
import sensing



fcsub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base"),
                               getSubTypeList(controller.FlightController)))
ccsub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base"),
                               getSubTypeList(controller.ChannelController)))
csub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base")
                                          and cls.__name__ not in ("FlightController", "ChannelController")
                                          and cls not in chain(fcsub, ccsub),
                              getSubTypeList(controller.Controller)))
ssub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base"),
                              getSubTypeList(sensing.Sensor)))
esub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base"),
                              getSubTypeList(sensing.Evaluator)))
commsub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base"),
                                 getSubTypeList(communication.CommunicationInterface)))
modsub: list[type] = list(filter(lambda cls: cls.AVAILABLE and not cls.__name__.endswith("Base")
                                            and cls.__name__ not in ("FlightController", "ChannelController",
                                                                     "CommunicationInterface", "Controller", "Sensor",
                                                                     "Evaluator")
                                            and cls not in chain(fcsub, ccsub, csub, ssub, esub, commsub),
                                getSubTypeList(drone.Module)))

@cache
def getArgs(cls: type) -> dict[str, Any]:
    """ Get the arguments of a class """
    args = cls.ARGS.copy() if hasattr(cls, "ARGS") else {}
    if not hasattr(cls, "_asyncProcess") or cls._asyncProcess == Module._asyncProcess:
        del args["interval"]
    return None if not args else args

def dictUpdate(d: dict, u: dict) -> dict:
    """ Update a dict with another dict """
    for k, v in u.items():
        if k in d:
            if isinstance(v, dict):
                d[k] = dictUpdate(d[k], v)
            else:
                d[k] = v
    return d

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
            "configuration": {k.__name__: getArgs(k)
                              for k in chain(fcsub, ccsub, csub, ssub, esub, commsub, modsub) if getArgs(k)},
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

    OVERRIDE: bool = False

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
            self.__defaults(file, self.__dict if not self.OVERRIDE else None)
        if not self.__available(self.AVAILABLE):
            d = self.__dict.copy()
            for k, v in d["modules"].items():
                if k == "flight" and v not in self.AVAILABLE[k]:
                    d["modules"][k] = "FlightlessFlightController"
                elif k != "flight":
                    d["modules"][k] = list(filter(lambda x: x in self.AVAILABLE[k], v))
            self.__defaults(file, d, AttributeError("Requested modules not available"))
    
    def __defaults(self, file: str, update=None,
                   ae: AttributeError = AttributeError("Configuration file bad, loading defaults")):
        if update is None:
            update = {}
        os.replace(file, file.replace(".yml", ".backup.yml", 1).replace(".yaml", ".backup.yaml", 1))
        yaml.write(dictUpdate(Configuration.SPEC.copy(), update), file)
        raise ae
    
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
