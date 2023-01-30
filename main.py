from communication.Command import Command
from communication.CommandData import CommandData
from compatibility.ConsoleColor import ConsoleColor as CC, ConsoleStyle as CS, wrap
from compatibility.Itertools import chain
from compatibility.OS import path, os
from compatibility.Sys import sys, argv
from compatibility.Time import sleep, now
from compatibility.Types import TracebackType
from compatibility.Typing import Any, Optional, Type, Callable
from compatibility.AirSim import airsimClient, available as AirSimAvailable
from drone.Module import Module
from drone.PartialDroneData import PartialDroneData
from drone.UAV import UAV
from utils.CLI import Executor, CLI, helptext
from utils.Configuration import Configuration
from utils.Logger import Logger, _Logging
from utils.Subtypes import getSubTypeList
from utils.SysInfo import InfoCache
from utils.events.Event import Event
from utils.events.EventType import EventType
from utils.math.Vector import Vector3


class Main(Executor):
    VERSION: str = "0.2.1"
    """ Software version to print """
    EXIT_CALL: Callable = None
    KILL: bool = False
    CONFIG_FILE: str = ""
    HEADLESS: bool = False

    def __init__(self):
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
        for i in range(3):
            try:
                self.__configuration: Configuration = Configuration(Main.CONFIG_FILE)
            except AttributeError as aError:
                Configuration.OVERRIDE = bool(i)
                self._logger.error(aError)
                if i == 2:
                    self._logger.write("Could not load Configuration")
                    self._exit()
                else:
                    self._logger.write("Trying again...")
        self.__uav: UAV = UAV(self.__configuration.data)

    def start(self):
        self.__uav.notify(Event(EventType.POWER_UP, self.__uav.data))
        if AirSimAvailable:
            airsimClient.passArguments(self.__configuration.data.configuration("AirSimFlightController"),
                                       Logger("AirSimClient"))
        self.__initializeModules()
        self.__uav.notify(Event(EventType.INITIALIZATION, self.__uav.data))
        sys.excepthook = self.__exceptionHook
        if not Main.HEADLESS:
            self.__cli.start()
        for thread in chain(*self.__modules.values()):
            try:
                thread.join()
            except RuntimeError:
                pass
    
    def __initializeModules(self):
        moduleCollection: dict[str, set[str]] = self.__configuration.moduleCollection
        self.__modules = {cat: [self.__findModule(module, Module)
                                (self.__uav, Logger(module), self.__configuration.data)
                                for module in modules]
                          for cat, modules in moduleCollection.items()}
    
    @staticmethod
    def __exceptionHook(eType: Type[BaseException], e: BaseException, trace: Optional[TracebackType] = None):
        Logger.error(e)
        Main.EXIT_CALL("Exiting due to an exception")

    @staticmethod
    def __findModule(moduleName: str, superclass: Any) -> type(Module):
        for cls in getSubTypeList(superclass):
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
            Logger("__main__").print(wrap(msg, CC.F.RED, CS.BRIGHT))
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
            Logger("__main__").print(wrap(msg, CC.F.RED, CS.BRIGHT))
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
                "takeOffAltitude": float(args[0]),
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
        pos: Vector3 = Vector3(*map(float, args[:3])) + self.__uav.data.position * relative
        dd: dict[str, Any] = {"target": pos, "speed": 5}
        self.__uav.notify(Event(EventType.COMMAND_CHANGE_COURSE, CommandData(cmd=Command.CHANGE_COURSE, msg=dd)))


def main(*args: str):
    while not Main.KILL:
        l: int = len(args)
        for arg in args:
            if arg.startswith("--"):
                arg = arg[2:]
                if arg.lower() == "headless":
                    Main.HEADLESS = True
                l -= 1
            elif path.isfile(arg) and not Main.CONFIG_FILE:
                Main.CONFIG_FILE = arg

        dir: str = path.join(_Logging.DIR,  f"{now().strftime('%Y-%m-%d %H-%M-%S')} ({path.basename(' '.join(args))})")
        """ The directory to save these instances logs in: """
        if not path.isdir(dir):
            os.mkdir(dir)  # Create the directory if it does not exist
        _Logging.DIR = dir

        if not Main.CONFIG_FILE:
            Logger("__main__").write(f"Configuration file {'does not exist' * l}{'missing as argument' * (not l)}"
                                     f", using config.yml")
            Main.CONFIG_FILE = "config.yml"

        siLogger: Logger = Logger("SysInfo")
        for Exception in InfoCache.getImportErrors():
            siLogger.error(Exception)
        Main().start()


if __name__ == "__main__":
    main(*argv[1:])
    os.environ["PYTHONHASHSEED"] = "random"

