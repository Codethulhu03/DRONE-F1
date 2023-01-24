from compatibility.Subprocess import Popen
from compatibility.Typing import Any, Optional
from compatibility.AirSim import airsimClient, available, RPCError
from compatibility.Json import dumps
from compatibility.OS import os
from compatibility.Psutil import processIter, available as psavailable
from communication.CommandData import CommandData
from controller.FlightController import FlightController
from drone import DroneData
from drone.DroneState import DroneState
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import process, evaluate
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.math.Coordinates import Coordinates
from utils.math.Vector import Vector3


class AirSimFlightController(FlightController):
    AVAILABLE: bool = available
    """ Whether the Module is available (imports were successful) """
    ARGS: dict[str, Any] = {**FlightController.ARGS,
            "name"                  : "",
            "ip"                    : "",
            "port"                  : 41451,
            "timeoutValue"          : 3600000,
            "autoLaunchAirsim"      : False,
            "forceCloseAirsimOnExit": False,
            "sensorFrequency"       : 0.5,
            "useEnvironmentHome"    : True,
            "environmentConfig"     : {
                    "airsimBinaryPath": "",
                    "resolution"      : [1280, 720],
                    "defineConfigHere": False,
                    "viewMode"        : "FlyWithMe",
                    "wind"            : [0, 0, 0]
                    },
            "home"                    : {"X":0, "Y":0, "Z":0},
            }
    """ Arguments for the configuration file """
    if AVAILABLE:
        def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
            FlightController.__init__(self, mediator, logger, configData)
            self._config = configData.ownArguments
            self.__home: Vector3 = Vector3(self._config["home"]["X"], self._config["home"]["Y"],
                                           self._config["home"]["Z"])
            self.__connected = False
            self._airsim: Optional[airsimClient] = None
        
        @process(EventType.INITIALIZATION)
        def _initialize(self, data: Optional[DroneData]):
            if not self.__connected:
                self.__connected = True
                if self._config["autoLaunchAirsim"]:
                    self._launchAirSim()
                self._airsim = airsimClient.getClient()
                try:
                    self._airsim.enableApiControl(
                        True, vehicle_name=self._config["name"])
                except RPCError:
                    self._config["name"] = ""
                    self._airsim.enableApiControl(True)
                if self._config["useEnvironmentHome"]:
                    geo = self._airsim.getHomeGeoPoint(
                            vehicle_name=self._config["name"])
                    self._home = Coordinates(geo.latitude, geo.longitude)
            return super()._initialize(data)
        
        def deactivate(self, kill: bool = False):
            if self._airsim:
                self._airsim.enableApiControl(False, vehicle_name=self._config["name"])
                if self._config["forceCloseAirsimOnExit"] and psavailable:
                    for proc in processIter():
                        # check whether the process name matches
                        if proc.name() == self._binaryName:
                            proc.kill()
                    self._airsimProcess.kill()
            FlightController.deactivate(self)
        
        def _launchAirSim(self):
            binaryPath = self._config["environmentConfig"]["airsimBinaryPath"]
            self._binaryName = os.path.basename(binaryPath)
            if not os.access(binaryPath, os.X_OK):
                self._logger.print(
                        "Your specified AirSim binary path isn't executable or doesn't exist")
                return
            settings = {}
            if self._config["environmentConfig"]["defineConfigHere"]:
                wind = self._config["environmentConfig"]["wind"]
                settings = {
                        "SettingsVersion": 1.2,
                        "SimMode"        : "Multirotor",
                        "ViewMode"       : self._config["environmentConfig"]["viewMode"],
                        "Wind"           : {
                                "X": wind[0],
                                "Y": wind[1],
                                "Z": wind[2]
                                }
                            
                        }
                settings = dumps(settings).replace(" ", "")
            resolution = self._config["environmentConfig"]["resolution"]
            self._airsimProcess = Popen(
                    [binaryPath, f"-ResX={resolution[0]}", f"-ResY={resolution[1]}", "-windowed", f"--settings={settings}"])
        
        @process(EventType.COMMAND_ARM)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _arm(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            self._airsim.armDisarm(True, vehicle_name=self._config["name"])
            return PartialDroneData({"state": DroneState.IDLE})
        
        @process(EventType.COMMAND_DISARM)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _disarm(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            self._airsim.armDisarm(False, vehicle_name=self._config["name"])
            return PartialDroneData({"state": DroneState.DISARMED})
        
        @process(EventType.COMMAND_START)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _takeOff(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            self._airsim.enableApiControl(True, vehicle_name=self._config["name"])
            self._airsim.takeoffAsync(vehicle_name=self._config["name"])
            self._airsim.moveToZAsync(
                    -data.msg["takeOffAltitude"], data.msg["speed"], vehicle_name=self._config["name"])
            return PartialDroneData({"state": DroneState.AT_START})
        
        @process(EventType.COMMAND_POS_HOLD)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _holdPosition(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            self._airsim.hoverAsync(vehicle_name=self._config["name"])
            return PartialDroneData({"state": DroneState.POS_HOLD})
        
        @process(EventType.COMMAND_RTL)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _returnToLaunch(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            self._airsim.moveToPositionAsync(
                    0, 0, -data.msg["altitude"], data.msg["speed"], vehicle_name=self._config["name"])
            return PartialDroneData({"state": DroneState.RTL})
        
        @process(EventType.COMMAND_LAND)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _land(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            self._airsim.enableApiControl(True, vehicle_name=self._config["name"])
            self._airsim.moveToZAsync(-1, 5,
                                      vehicle_name=self._config["name"]).join()
            self._airsim.landAsync(
                    timeout_sec=3e+38, vehicle_name=self._config["name"])
            return PartialDroneData({"state": DroneState.LAND})
        
        @process(EventType.COMMAND_CHANGE_COURSE)
        @evaluate(EventType.DRONE_DATA_UPDATE)
        def _goto(self, data: CommandData) -> PartialDroneData:
            if not self.__connected:
                return PartialDroneData()
            target = data.msg["target"]
            if self._currentTarget != target:
                self._airsim.enableApiControl(True, vehicle_name=self._config["name"])
                self._airsim.moveToPositionAsync(
                        target[0] - self.__home[0], target[1] - self.__home[1], -target[2] + self.__home[2],
                        data.msg["speed"], vehicle_name=self._config["name"])
                self._currentTarget = target
                self._route.append(target)
            return PartialDroneData({"state": DroneState.FLYING_TO_GOAL, "currentTarget": target})
