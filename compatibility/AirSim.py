
available: bool = True
try:
    from compatibility.Typing import Optional
    import airsim as airsimCompatability
    import airsim.types as airsimTypesLib

    from utils.Data import Data
    from utils.Logger import Logger
    from utils.HiddenPrints import HiddenPrints

    airsim = airsimCompatability
    airsimTypes = airsimTypesLib
    
    
    class AirSimClient:
        
        def __init__(self):
            self.__argumentsPassed = False
            self.__config: Data = None
            self.__logger: Logger = None
        
        def passArguments(self, config: Data, logger: Logger):
            self.__config = config
            self.__logger = logger
            self.__argumentsPassed = True
        
        def getClient(self) -> Optional[airsim.MultirotorClient]:
            if not self.__argumentsPassed:
                self.__logger.write("AirSim Arguments weren't passed")
                raise ValueError
            ip = self.__config["ip"]
            port = self.__config["port"]
            timeoutValue = self.__config["timeoutValue"]
            
            client = airsim.MultirotorClient(ip, port, timeoutValue)
            with HiddenPrints():
                try:
                    client.confirmConnection()
                except Exception as e:
                    self.__logger.write("Couldn't connect to Airsim. Reason: " + str(e))
                    return
                self.__logger.write("Connected to AirSim.")
            return client
    
    
    airsimClient: AirSimClient = AirSimClient()
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    airsim = None
    airsimTypes = None
    AirSimClient = None
