from utils.Data import Data

from communication.CommandData import CommandData
from drone.DroneData import DroneData
from drone.PartialDroneData import PartialDroneData
from sensing.SensorData import SensorData
from sensing.RawData import RawData

def __getSubTypeList(t: type) -> list[type]:
    l: list[type] = t.__subclasses__()
    for sub in l:
        l += __getSubTypeList(sub)
    return l

DATA_TYPES: list[type] = sorted(__getSubTypeList(Data) + [Data], key=lambda x: x.__name__)
