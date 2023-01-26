from utils.Data import Data
from utils.Subtypes import getSubTypeList

from communication.CommandData import CommandData
from drone.DroneData import DroneData
from drone.PartialDroneData import PartialDroneData
from sensing.SensorData import SensorData
from sensing.RawData import RawData

DATA_TYPES: list[type] = sorted(getSubTypeList(Data) + [Data], key=lambda x: x.__name__)
