from compatibility.Inspect import stack as inspectStack, getmodulename

from utils.Data import Data


class ConfigurationData(Data):
    TYPES = dict(Data.TYPES, **{
            "mission"      : str,
            "drone"        : dict,
            "configuration": dict
            })
    """ TYPES of underlying dict for checking validity of Instance (see :attribute:`utils.Data.Data.TYPES`) """
    
    @property
    def mission(self) -> str:
        return self["mission"]
    
    @property
    def drone(self) -> Data:
        return self["drone"]
    
    @property
    def ownArguments(self) -> Data:
        lastEl: str = ""
        for el in inspectStack():
            modName: str = "Main"
            try:
                modName = str(el[0].f_locals["self"].__class__.__name__)
            except KeyError:
                try:
                    modName = str(el[0].f_locals["args"].__class__.__name__)
                except KeyError:
                    modName = getmodulename(el[1])
            if modName in ("Main", "main"):
                break
            lastEl = modName
        return self.configuration(lastEl)
    
    def configuration(self, cls: str) -> Data:
        return self["configuration"][cls]
