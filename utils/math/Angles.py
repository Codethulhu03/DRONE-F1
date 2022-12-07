from compatibility.Math import atan2, pi, asin
from utils.math.Vector import Vector3


def eulerFromQuaternion(x: float, y: float, z: float, w: float) -> Vector3:
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x ** 2 + y ** 2)
    rollX = atan2(t0, t1) * 180 / pi
    rollX = formatDegreeTo360(rollX)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = max(t2, -1.0)
    pitchY = asin(t2) * 180 / pi
    pitchY = formatDegreeTo360(pitchY)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y ** 2 + z ** 2)
    yawZ = atan2(t3, t4) * 180 / pi
    yawZ = formatDegreeTo360(yawZ)
    
    return Vector3(rollX, pitchY, yawZ)


def formatDegreeTo360(deg: float) -> float:
    return 360 + deg if deg < 0 else deg
