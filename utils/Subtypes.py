def getSubTypeList(t: type) -> list[type]:
    l: list[type] = t.__subclasses__()
    for sub in l:
        l += getSubTypeList(sub)
    return l