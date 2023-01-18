import communication
import controller
import drone
import sensing
from communication.Command import Command
from communication.CommandData import CommandData
from compatibility.ConsoleColor import ConsoleColor as CC, ConsoleStyle as CS, wrap
from compatibility.Itertools import chain
from compatibility.OS import path, os
from compatibility.Platform import system
from compatibility.Sys import sys, argv
from compatibility.Time import sleep
from compatibility.Types import TracebackType
from compatibility.Typing import Any, Optional, Type, Callable
from compatibility.AirSim import airsimClient, available as AirSimAvailable
from drone.Module import Module
from drone.PartialDroneData import PartialDroneData
from drone.UAV import UAV
from utils.CLI import Executor, CLI, helptext
from utils.Configuration import Configuration
from utils.Data import Data
from utils.Logger import Logger
from utils.events.Event import Event
from utils.events.EventType import EventType
from utils.math.Vector import Vector3

class Main(Executor):
    VERSION: str = "0.0.0"
    EXIT_CALL: Callable = None
    KILL: bool = False
    
    def __init__(self, config: str):
        super().__init__(Logger())
        Main.EXIT_CALL = self._exit
        self.__cli = CLI(self, self._logger)
        self.__modules: dict[str, list[Module]] = {
                "flight"       : [],
                "channels"     : [],
                "controllers"  : [],
                "sensors"      : [],
                "evaluators"   : [],
                "communication": [],
                "unknown"      : []
                }
        for i in range(2):
            try:
                self.__configuration: Configuration = Configuration(config)
            except AttributeError as aError:
                self._logger.write(aError)
                if i:
                    self._logger.write("Could not load Configuration")
                    self._exit()
                else:
                    self._logger.write("Trying again...")
        self.__uav: UAV = UAV(self.__configuration.data)
        self.__uav.notify(Event(EventType.POWER_UP, self.__uav.data))
        if AirSimAvailable:
            airsimClient.passArguments(self.__configuration.data.configuration("AirSimFlightController"),
                                       Logger("AirSimClient"))
        self.__initializeModules()
        self.__uav.notify(Event(EventType.INITIALIZATION, self.__uav.data))
        sys.excepthook = self.__exceptionHook
        self.__cli.start()
        for thread in chain(*self.__modules.values()):
            try:
                thread.join()
            except RuntimeError:
                pass
        sleep(0.5)
    
    def __initializeModules(self):
        moduleCollection: dict[str, set[str]] = self.__configuration.moduleCollection
        superclasses: dict[str, type] = {
                "flight"       : controller.FlightController,
                "channels"     : controller.ChannelController,
                "controllers"  : controller.Controller,
                "sensors"      : sensing.Sensor,
                "evaluators"   : sensing.Evaluator,
                "communication": communication.CommunicationInterface,
                "unknown"      : drone.Module
                }
        self.__modules = {cat: [self.__findModule(module, superclasses[cat])
                                (self.__uav, Logger(module), self.__configuration.data)
                                for module in modules]
                          for cat, modules in moduleCollection.items()}
    
    @staticmethod
    def __exceptionHook(eType: Type[BaseException], e: BaseException, trace: Optional[TracebackType] = None):
        Logger("exception").write(wrap(str(e), CC.F.RED, CS.BRIGHT))
        Logger("exception").log("\n".join((str(eType), str(trace))))
        Main.EXIT_CALL("Exiting due to an Exception")
    
    @staticmethod
    def __findModule(moduleName: str, superclass: Any) -> type(Module):
        for cls in superclass.__subclasses__():
            if cls.__name__ == moduleName:
                return cls
        raise AttributeError(f"Module {moduleName} not found")
    
    @helptext("show overview of all commands", "help messages selectable")
    def _help(self, *args: str) -> str:
        return self.__cli.help(*args)
    
    @helptext("activate modules", "modules selectable")
    def _start(self, *args: str, msg: str = "STARTING..."):
        modules = [x for moduleList in self.__modules.values() for x in moduleList if
                   not args or type(x).__name__ in args]
        if modules:
            self._logger.print(wrap(msg, CC.F.RED, CS.BRIGHT))
            for module in modules:
                module.activate()
        sleep(1)
        self.__uav.activate()
    
    @helptext("deactivate modules", "modules selectable")
    def _stop(self, *args: str, msg: str = "STOPPING...", kill: bool = False):
        modules = [x for moduleList in self.__modules.values() for x in moduleList if
                   not args or type(x).__name__ in args]
        self.__uav.deactivate()
        if modules:
            self._logger.print(wrap(msg, CC.F.RED, CS.BRIGHT))
            sleep(1)
            for module in modules:
                module.deactivate(kill)
        sleep(1)

    @helptext("reboot the program")
    def _reboot(self, msg: str = "REBOOTING..."):
        self.__uav.notify(Event(EventType.POWER_DOWN, self.__uav.data))
        self._stop(msg=msg, kill=True)
        self.__cli.stop()
    
    @helptext("exit the program safely")
    def _exit(self, msg: str = "EXITING..."):
        self._reboot(msg=msg)
        Main.KILL = True
    
    @helptext("show all installed modules", "modules selectable")
    def _modules(self, *args: str) -> str:
        categories = set(self.__modules.keys()).intersection(set(args))
        categories = self.__modules.keys() if not len(categories) else categories
        maxCat = max(len(cat) for cat in categories)
        return "\n".join(f"{wrap(cat.ljust(maxCat), CC.F.BLUE)}: {self.__modules[cat]}" for cat in categories)
    
    @helptext("show the current drone data", "data selectable", True)
    def _data(self, *args: str) -> str:
        return self.__uav.data if not args else PartialDroneData({k: v for k, v in self.__uav.data.items if k in args})
    
    @helptext("Send the command to take off", "Take off altitude")
    def _takeoff(self, *args: str):
        if not len(args):
            args = (5.,)
        self.__uav.notify(Event(EventType.COMMAND_START, CommandData(cmd=Command.START, msg={
                "takeOffAltitude": args[0],
                "speed"          : 5})))
    
    @helptext("Send the command to land")
    def _land(self):
        self.__uav.notify(Event(EventType.COMMAND_LAND, CommandData(cmd=Command.LAND, msg={})))
    
    @helptext("Send the next Waypoint for the drone", "Waypoint Coordinates | -r for relative Coordinates")
    def _goto(self, *args: str):
        relative: bool = False
        if "-r" in args:
            relative = True
            args = [x for x in args if x != "-r"]
        pos: Vector3 = Vector3([float(x) for x in args[:3]] + [0] * (3 - len(args))) + self.__uav.data.position * relative
        dd: dict[str, Any] = {"target": pos, "speed": 5}
        self.__uav.notify(Event(EventType.COMMAND_CHANGE_COURSE, CommandData(cmd=Command.CHANGE_COURSE, msg=dd)))


def main(*args: str):
    while not Main.KILL:
        log: Logger = Logger("__main__")
        l: int = len(args)
        if not l or not path.isfile(*args):
            log.write(f"Configuration file {'does not exist' * l}{'missing as argument' * (not l)}, using config.yml")
            args: tuple[str] = ("config.yml",)
        Main(*args)


if __name__ == "__main__":
    if not os.environ.get("PYTHONHASHSEED"):
        if system() != "Windows":
            os.environ["PYTHONHASHSEED"] = "25565"
            os.execv(sys.executable, [sys.executable, *sys.argv])  # restart python shell to apply the new seed
        else:
            print("[__main__]  Python hash seed not automatically changeable. Set the environment variable PYTHONHASHSEED for correct execution")
    print(f"[__main__]  Python hash seed: {os.environ.get('PYTHONHASHSEED')}")
    print(f"[__main__]  Python hash test: {hash('test')=}")
    print(f"[__main__]  If the hash values are different, communication won't work - I need to stop using hashes at some point")
    main(*argv[1:])
    os.environ["PYTHONHASHSEED"] = "random"

