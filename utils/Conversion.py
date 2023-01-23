from compatibility.Struct import unpack, pack
from compatibility.Typing import Any, get_origin, get_args, Callable, Union
from compatibility.Math import log2
from compatibility.Json import dumps, loads

DICT_TYPES: list[type] = [str, int]


def toBytes(d: Any) -> bytes:
    if isinstance(d, float):
        d = unpack('<Q', pack('<d', d))[0]
    if isinstance(d, int):
        return d.to_bytes(1 if abs(d) < 128 else int((log2(abs(d)) + 1) // 4), "big", signed=True)
    elif isinstance(d, dict):
        # Format: [len(key) (1 byte), key, type of value (index in tuple = 1 byte), length of value bytes, bytes]
        b: bytes = bytes()
        types = sorted(DICT_TYPES, key=lambda x: x.__name__)
        for k, v in d.items():
            if not isinstance(k, str):
                raise NotImplementedError("Damn it, gotta implement that afterall, huh?")
            if not type(v) in types:
                raise NotImplementedError(f"Okay, note to self: add {type(v)} to conversion")
            kb: bytes = toBytes(k)
            vb: bytes = toBytes(v)
            b += bytes([len(kb)]) + kb + bytes([types.index(type(v))]) + bytes([len(vb)]) + vb
        return b
    if isinstance(d, str):
        return d.encode("utf-8")
    elif isinstance(d, list):
        b: bytes = bytes()
        for x in d:
            xb = toBytes(x)
            b += bytes([len(xb)]) + xb
        return b
    return bytes(d)


def __dictf(i: int, b: bytes, keys: list) -> tuple[str, type, int]:
    kl: int = b[i]
    i += 1
    k: str = fromBytes(b[i: i + kl], str)
    vt: type = keys[b[kl]]
    i = kl + 1
    return k, vt, i


def __dataf(i: int, b: bytes, keys: list) -> tuple[str, type, int]:
    k, v = keys[b[i]]
    return k, v, i + 1


def __listf(i: int, b: bytes, keys: type) -> tuple[str, type, int]:
    return "", keys, i


def fill(data: Union[list, dict], b: bytes, keys: Union[list, type], f: Callable) -> dict[str, Any]:
    i: int = 0
    while i < len(b):
        k, vt, i = f(i, b, keys)
        r: int = i + 1 + b[i]
        i += 1
        v: Any = fromBytes(b[i:r], vt)
        if isinstance(data, dict):
            data[k] = v
        else:
            data.append(v)
        i = r
    return data


def fromBytes(b: bytes, t: type) -> Any:
    if t == int:
        return int.from_bytes(b, "big", signed=True)
    elif t == float:
        return unpack("<d", pack("<Q", int.from_bytes(b, "big", signed=True)))[0]
    elif t == dict:
        return fill({}, b, sorted(DICT_TYPES, key=lambda x: x.__name__), __dictf)
    elif t == str:
        return b.decode("utf-8")
    elif get_origin(t) == list:
        return fill([], b, get_args(t)[0], __listf)
    elif callable(getattr(t, "fromBytes", None)):
        return t.fromBytes(b)
    return t(b)


def dataDictFromBytes(types: dict, b: bytes) -> dict:
    keys: list[tuple[str, type]] = sorted(types.items())
    lb = b[0] + 1
    data = fill({}, b[1: lb], keys, __dataf)
    data.update(fromBytes(b[lb:], dict))
    return data


def jsonDumps(obj: Any) -> bytes:
    # if isinstance(obj, dict):
    #     return bytes().join([toBytes(v) for _, v in sorted(obj.items())])
    #     return bytes().join([toBytes(v) for v in obj])
    # elif isinstance(obj, (int, float, bool)):
    #     frm: str = "i" if isinstance(obj, int) else "f" if isinstance(obj, float) else "?"
    #     return pack(frm, obj)
    # elif callable(getattr(obj, "bytes", None)):
    #     return obj.bytes()
    # else:
    return dumps(obj, default=lambda o: o.toJson()).encode("utf-8")


def jsonLoads(obj: bytes) -> dict:
    return loads(obj.decode("utf-8"))
