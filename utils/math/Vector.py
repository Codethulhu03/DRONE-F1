from __future__ import annotations  # for using "Vector2" and "Vector3" in type annotations

from compatibility.Typing import Union  # for type annotations
from compatibility.Json import loads  # for loading json data
from compatibility.Math import acos, cos, sin, sqrt  # math stuff because math class
from utils import Conversion  # Conversion to bytes and back


class Vector2:
    """Class representing vectors in 2D space."""

    def __init__(self, x: Union[list, bytes, float] = 0.0, y: float = 0.0):
        l: list[float] = []
        if isinstance(x, bytes):
            if len(x) == 32:
                l = Conversion.fromBytes(x, list[float])
            else:
                l = Conversion.fromBytes(x, list[int])
        elif isinstance(x, list):
            l = x
        if l:
            x, y = l
        self.x = float(x)
        self.y = float(y)

    def __bytes__(self) -> bytes:
        return Conversion.toBytes(self.toList())

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Union[float, int, bool] | Vector2) -> Vector2 | float:
        if isinstance(other, (float, int, bool)):
            return Vector2(self.x * other, self.y * other)
        elif isinstance(other, Vector2):
            return self.dot(other)
        else:
            raise TypeError("unsupported operand type(s) for *: 'Vector3' and '%s'" % type(other).__name__)

    def __truediv__(self, other: Union[float, int, bool]) -> Vector2:
        return Vector2(self.x / other, self.y / other)

    def rotate(self, angle: float) -> Vector2:
        return Vector2(cos(angle) * self.x - sin(angle) * self.y, sin(angle) * self.x + cos(angle) * self.y)

    @property
    def magnitude(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> Vector2:
        return self / self.magnitude

    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y

    def angle(self, other: Vector3) -> float:
        return acos(self.dot(other) / (self.magnitude * other.magnitude))

    def cross(self, other: Vector2) -> float:
        return self.x * other.y - self.y * other.x

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: Vector2) -> bool:
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: Vector2) -> bool:
        return self.x != other.x or self.y != other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __getitem__(self, key: int) -> float:
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

    def __setitem__(self, key: int, value: float) -> None:
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError("Index out of range")

    def __iter__(self) -> Vector2:
        yield self.x
        yield self.y

    def __len__(self) -> int:
        return 2

    def __bool__(self) -> bool:
        return bool(self.x or self.y)

    def __contains__(self, item: float) -> bool:
        return item in (self.x, self.y)

    def rotate2(self, other: Union[float, int, bool]) -> Vector3:
        return Vector3(self.x * cos(other) - self.y * sin(other),
                       self.x * sin(other) + self.y * cos(other))

    def __matmul__(self, other: Union[float, int, bool]) -> Vector2:
        return self.rotate2(other)

    def __and__(self, other: Vector2) -> float:
        return self.cross(other)

    def __or__(self, other: Vector2) -> float:
        return self.angle(other)

    def __abs__(self) -> float:
        return self.magnitude

    def toList(self):
        if all(int(n) == n for n in [self.x, self.y]):
            return [int(self.x), int(self.y)]
        return [self.x, self.y]


class Vector3(Vector2):
    """Class representing vectors in 3D space."""

    def __init__(self, x: Union[float, bytes, list] = 0.0, y: float = 0.0, z: float = 0.0):
        l: list[float] = []
        if isinstance(x, bytes):
            if len(x) == 48:
                l = Conversion.fromBytes(x, list[float])
            else:
                l = Conversion.fromBytes(x, list[int])
        elif isinstance(x, list):
            l = x
        if l:
            x, y, z = l
        super().__init__(x, y)
        self.z: float = float(z)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: Vector3) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other: Vector3) -> bool:
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: Union[float, int, bool] | Vector3) -> Vector3 | float:
        if isinstance(other, (float, int, bool)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vector3):
            return self.dot(other)
        else:
            raise TypeError("unsupported operand type(s) for *: 'Vector3' and '%s'" % type(other).__name__)

    def __truediv__(self, other: Union[float, int, bool]) -> Vector3:
        return Vector3(self.x / other, self.y / other, self.z / other)

    @property
    def magnitude(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self) -> Vector3:
        return self / self.magnitude

    def dot(self, other: Vector3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3) -> Vector3:
        return Vector3(self.y * other.z - self.z * other.y,
                       self.z * other.x - self.x * other.z,
                       self.x * other.y - self.y * other.x)

    def rotate2(self, other: Union[float, int, bool]) -> Vector3:
        return Vector3(self.x * cos(other) - self.y * sin(other),
                       self.x * sin(other) + self.y * cos(other), self.z)

    def rotate(self, other: Vector3) -> Vector3:
        pitch: float = other.x
        yaw: float = other.y
        roll: float = other.y
        # roll (x-axis rotation)
        x: float = self.x
        y: float = self.y * cos(roll) - self.z * sin(roll)
        z: float = self.y * sin(roll) + self.z * cos(roll)

        # pitch (y-axis rotation)
        x = x * cos(pitch) + z * sin(pitch)
        y = y
        z = -x * sin(pitch) + z * cos(pitch)

        # yaw (z-axis rotation)
        x = x * cos(yaw) - y * sin(yaw)
        y = x * sin(yaw) + y * cos(yaw)
        z = z

        return Vector3(x, y, z)

    def angle(self, other: Vector3) -> float:
        return acos(self.similarity(other))

    def inBounds(self, minV: Vector3, maxV: Vector3) -> bool:
        return minV.x <= self.x <= maxV.x and minV.y <= self.y <= maxV.y and minV.z <= self.z <= maxV.z

    def similarity(self, other: Vector3) -> float:
        m: float = (self.magnitude * other.magnitude)
        if not m:
            return -1
        return (self * other) / (self.magnitude * other.magnitude)

    def __getitem__(self, item) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError("Vector3 index out of range")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Vector3 index out of range")

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __len__(self) -> int:
        return 3

    def __contains__(self, item) -> bool:
        return item in (self.x, self.y, self.z)

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0 or self.z != 0

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    def __lt__(self, other: Vector3) -> bool:
        return self.magnitude < other.magnitude

    def __le__(self, other: Vector3) -> bool:
        return self.magnitude <= other.magnitude

    def __gt__(self, other: Vector3) -> bool:
        return self.magnitude > other.magnitude

    def __ge__(self, other: Vector3) -> bool:
        return self.magnitude >= other.magnitude

    @staticmethod
    def fromJson(jsonString: str) -> Vector3:
        return Vector3(*loads(jsonString))

    def toList(self) -> list:
        if all(int(n) == n for n in [self.x, self.y, self.z]):
            return [int(self.x), int(self.y), int(self.z)]
        return [self.x, self.y, self.z]

    def projectOn(self, other: Vector3) -> Vector3:
        return other * (self.dot(other) / other.magnitude)

    def toJson(self) -> list:
        return self.toList()

    def __matmul__(self, other: Union[float, int, bool]) -> Vector2:
        return self.rotate2(other)

    def __and__(self, other: Vector3) -> Vector3:
        return self.cross(other)

    def __or__(self, other: Vector3) -> float:
        return self.angle(other)

    def __abs__(self) -> float:
        return self.magnitude
