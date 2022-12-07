from __future__ import annotations  # for using "Coordinates" in type annotations

from compatibility.Json import loads  # for loading json data
from compatibility.Math import sin, cos, atan2, sqrt, degrees, radians  # math stuff because math class
from compatibility.Typing import Union  # for type annotations
from utils import Conversion  # Conversion to bytes and back
from utils.math.Vector import Vector3, Vector2  # for calculations with vectors

EARTH_RADIUS = 6378137.0
""" Radius of the earth in meters. """


class Coordinates:
    """ Class representing GPS coordinates """
    
    def __init__(self, lat: Union[float, bytes] = 0.0, lon: float = 0.0, alt: float = 0.0):
        """
        Initialize a new Coordinates object.
        
        :param lat: Latitude in degrees (or bytes for deserialization)
        :param lon: Longitude in degrees
        :param alt: Altitude in meters above sea level
        """
        if isinstance(lat, bytes):
            lat, lon, alt = Conversion.fromBytes(lat, list[float])  # Convert bytes to list of floats and unpack it
        self.__lat: float = lat
        """ Latitude in degrees """
        self.__lon: float = lon
        """ Longitude in degrees """
        self.__alt: float = alt
        """ Altitude in meters above mean sea level """
    
    def __eq__(self, other) -> bool:
        """
        Check if two coordinates are equal
        :param other: The other coordinates
        :return: True if the coordinates are equal, False otherwise
        """
        return self.__lat == other.__lat and self.__lon == other.__lon and self.__alt == other.__alt
    
    def __repr__(self) -> str:
        """ Get a string representation of the coordinates """
        return str((self.__lat, self.__lon, self.__alt))
    
    def toList(self) -> list:
        """ Get a list representation of the coordinates """
        return [self.__lat, self.__lon, self.__alt]
    
    toJson = toList
    
    def __bytes__(self) -> bytes:
        """
        Convert the coordinates to bytes
        
        :return: Bytes object representing the coordinates
        """
        return Conversion.toBytes(self.toList())
    
    @staticmethod
    def fromJson(jsonString: str) -> Coordinates:
        """
        Create a new Coordinates object from a json string.
        
        :param jsonString: The json string
        :return: The constructed Coordinates object
        """
        return Coordinates(*loads(jsonString))
    
    @property
    def lat(self) -> float:
        """
        Get Latitude in degrees
        
        :return: Latitude in degrees
        """
        return self.__lat
    
    @property
    def lon(self) -> float:
        """
        Get Longitude in degrees
        
        :return: Longitude in degrees
        """
        return self.__lon
    
    @property
    def alt(self) -> float:
        """
        Get altitude in meters above mean sea level
        
        :return: Altitude in meters above mean sea level
        """
        return self.__alt
    
    def __add__(self, other: Vector2) -> Coordinates:
        """
        Add a vector to the coordinates (move x meters north, y meters east and z meters up)
        
        :param other: The vector to add
        :return: The moved coordinates
        
        .. seealso:: :func:`move`
        """
        return self.move(*other)
    
    def __sub__(self, other: Coordinates) -> float:
        """
        Return the distance between two coordinates
        
        :param other: The other coordinates
        :return: The distance between the two coordinates
        
        .. seealso:: :func:`distance`
        """
        if isinstance(other, Coordinates):
            return self.distance(other)
    
    def __or__(self, other: Coordinates) -> Coordinates:
        """
        Calculate the middle between two coordinates
        
        :param other: The other coordinates
        :return: The middle coordinates
        
        .. seealso:: :func:`midpoint`
        """
        if isinstance(other, Coordinates):
            return self.midpoint(other)
    
    def distance(self, coordinates: Coordinates) -> float:
        """
        Calculate the distance between two coordinates
        
        :param coordinates: The other coordinates
        :return: The distance between the two coordinates
        """
        sLat: float = radians(self.__lat)
        sLon: float = radians(self.__lon)
        oLat: float = radians(coordinates.__lat)
        oLon: float = radians(coordinates.__lon)
        a: float = sin((oLat - sLat) / 2) ** 2 + cos(sLat) * cos(oLat) * sin((oLon - sLon) / 2) ** 2
        return EARTH_RADIUS * 2 * atan2(sqrt(a), sqrt(1 - a))
    
    def midpoint(self, coordinates: Coordinates) -> Coordinates:
        """
        Calculate the middle between two coordinates
        
        :param coordinates: The other coordinates
        :return: The middle coordinates
        """
        sLat: float = radians(self.__lat)
        oLat: float = radians(coordinates.__lat)
        dLat: float = oLat - sLat
        bX: float = cos(oLat) * cos(dLat)
        bY: float = cos(oLat) * sin(dLat)
        return Coordinates(atan2(sin(sLat) + sin(oLat), sqrt((cos(sLat) + bX) ** 2 + bY ** 2)),
                           radians(self.__lon) + atan2(bY, cos(sLat) + bX))
    
    def calculateBearing(self, coordinates: Coordinates) -> float:
        """
        Calculate the bearing between two coordinates
        
        :param coordinates: The other coordinates
        :return: The bearing between the two coordinates in degrees
        """
        sLat: float = radians(self.__lat)
        oLat: float = radians(coordinates.__lat)
        dLon: float = radians(coordinates.__lon - self.__lon)
        return degrees(atan2(sin(dLon) * cos(oLat), cos(sLat) * sin(oLat) - (sin(sLat) * cos(oLat) * cos(dLon)))) % 360
    
    def move(self, dNorth: float, dEast: float, dHeight: float = 0.0) -> Coordinates:
        """
        Move x meters north, y meters east and z meters up
        
        :param dNorth: Distance in meters to move north
        :param dEast: Distance in meters to move east
        :param dHeight: Distance in meters to move up
        :return: The moved coordinates
        """
        return Coordinates(self.__lat + degrees(dNorth / EARTH_RADIUS),
                           self.__lon + degrees(dEast / (EARTH_RADIUS * cos(radians(self.__lon)))),
                           self.__alt + dHeight)
    
    def calcPositionalVector(self, origin: Coordinates) -> Vector3:
        """
        Calculate the positional vector from the origin to the coordinates
        
        :param origin: The origin coordinates
        :return: The positional vector
        """
        return Vector3(radians(self.__lat - origin.__lat) * EARTH_RADIUS,
                       radians(self.__lon - origin.__lon) * (EARTH_RADIUS * cos(radians(origin.__lon))),
                       self.__alt - origin.__alt)
