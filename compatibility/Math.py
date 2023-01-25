from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from math import (cos as mathCos, acos as mathAcos, sin as mathSin, atan2 as mathAtan2, radians as mathRadians,
                      sqrt as mathSqrt, degrees as mathDegrees, pi as mathPi, log2 as mathLog2, exp as mathExp,
                      asin as mathAsin)
    
    pi: float = mathPi
    sqrt = mathSqrt
    degrees = mathDegrees
    radians = mathRadians
    cos = mathCos
    sin = mathSin
    acos = mathAcos
    asin = mathAsin
    atan2 = mathAtan2
    exp = mathExp
    log2 = mathLog2
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    pi = 0.
    sqrt = notImplemented
    degrees = notImplemented
    radians = notImplemented
    cos = notImplemented
    sin = notImplemented
    acos = notImplemented
    asin = notImplemented
    atan2 = notImplemented
    exp = notImplemented
    log2 = notImplemented
