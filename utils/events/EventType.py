from __future__ import annotations

from compatibility.Enum import Enum


class EventTypeID:
    
    def __init__(self, hexID: int, dataType: str):
        self.__id: int = hexID
        self.__dataType: str = dataType
    
    @property
    def id(self):
        return self.__id
    
    @property
    def type(self):
        return self.__dataType


class EventType(Enum):
    
    @staticmethod
    def set() -> list[list[str]]:
        return [x for x in ([eType.name for eType in EventType if eType.value.id // 16 == i] for i in range(16)) if x]
    
    def __repr__(self):
        return self.name
    
    def type(self) -> str:
        return self.value.type
    
    @staticmethod
    def fromBytes(b: bytes) -> EventType:
        """ Return first EventType with matching id """
        return next((eType for eType in EventType if eType.value.id == b[0]), None)
        
    # Drone States = 0x0X
    POWER_UP = EventTypeID(0x00, "drone.DroneData.DroneData")
    POWER_DOWN = EventTypeID(0x01, "drone.DroneData.DroneData")
    INITIALIZATION = EventTypeID(0x02, "drone.DroneData.DroneData")
    IDLE = EventTypeID(0x03, "drone.DroneData.DroneData")
    AT_START = EventTypeID(0x04, "drone.DroneData.DroneData")
    AT_GOAL = EventTypeID(0x05, "drone.DroneData.DroneData")
    AT_WAYPOINT = EventTypeID(0x06, "drone.DroneData.DroneData")
    POS_HOLD = EventTypeID(0x07, "drone.DroneData.DroneData")
    LAND = EventTypeID(0x08, "drone.DroneData.DroneData")
    FLYING_TO_GOAL = EventTypeID(0x09, "drone.DroneData.DroneData")
    AVOIDING_COLLISION = EventTypeID(0x0A, "drone.DroneData.DroneData")
    FLOCK = EventTypeID(0x0B, "drone.DroneData.DroneData")
    EMERGENCY = EventTypeID(0x0C, "drone.DroneData.DroneData")
    RTL = EventTypeID(0x0D, "drone.DroneData.DroneData")
    DISARMED = EventTypeID(0x0E, "drone.DroneData.DroneData")
    ARM = EventTypeID(0x0F, "drone.DroneData.DroneData")
    
    # Commands = 0x1X
    COMMAND_START = EventTypeID(0x10, "communication.CommandData.CommandData")
    COMMAND_POS_HOLD = EventTypeID(0x11, "communication.CommandData.CommandData")
    COMMAND_CHANGE_COURSE = EventTypeID(0x12, "communication.CommandData.CommandData")
    COMMAND_LAND = EventTypeID(0x13, "communication.CommandData.CommandData")
    COMMAND_RTL = EventTypeID(0x14, "communication.CommandData.CommandData")
    COMMAND_STOP = EventTypeID(0x15, "communication.CommandData.CommandData")
    COMMAND_ARM = EventTypeID(0x16, "communication.CommandData.CommandData")
    COMMAND_DISARM = EventTypeID(0x17, "communication.CommandData.CommandData")
    
    # Communication = 0x2X
    PACKET_SENT = EventTypeID(0x20, "communication.Packet.Packet")
    PACKET_RECEIVED = EventTypeID(0x21, "communication.Packet.Packet")
    SEND_PACKET = EventTypeID(0x22, "communication.Packet.Packet")
    
    # Sensing = 0x3X
    RAW_SENSOR_DATA = EventTypeID(0x30, "sensing.RawData.RawData")
    MOVEMENT_SENSOR_DATA = EventTypeID(0x31, "sensing.SensorData.SensorData")
    MISC_SENSOR_DATA = EventTypeID(0x32, "sensing.SensorData.SensorData")
    MORSE_SENSOR_DATA = EventTypeID(0x33, "sensing.SensorData.SensorData")
    DRONE_DATA_UPDATE = EventTypeID(0x34, "drone.PartialDroneData.PartialDroneData")
    MOVEMENT_DATA_UPDATE = EventTypeID(0x35, "drone.PartialDroneData.PartialDroneData")
    AIRSIM_SENSOR_DATA = EventTypeID(0x36, "sensing.SensorData.SensorData")
    MAVSDK_SENSOR_DATA = EventTypeID(0x37, "sensing.SensorData.SensorData")
    DIGITAL_TWIN_SENSOR_DATA = EventTypeID(0x38, "sensing.SensorData.SensorData")
    
    # GoPro = 0x4x
    GOPRO_TAKE_PICTURE = EventTypeID(0x40, "communication.CommandData.CommandData")
    GOPRO_START_VIDEO = EventTypeID(0x41, "communication.CommandData.CommandData")
    GOPRO_STOP_VIDEO = EventTypeID(0x42, "communication.CommandData.CommandData")
    GOPRO_DOWNLOAD_FILE = EventTypeID(0x40, "communication.CommandData.CommandData")
    GOPRO_SET_PRESET = EventTypeID(0x40, "communication.CommandData.CommandData")
