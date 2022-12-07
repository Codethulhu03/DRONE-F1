from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from typing import (TypeVar as ttypevar, Callable as tcallable, Any as tany, Optional as toptional,
                        SupportsIndex as tsi, Collection as tcollection, ItemsView as tiv, List as tlist,
                        Iterable as titerable, Union as tunion, Dict as tdict, get_origin as tgo, get_args as tga,
                        Mapping as tmap, Type as ttype)
    
    TypeVar = ttypevar
    Callable = tcallable
    Any = tany
    Optional = toptional
    SupportsIndex = tsi
    Collection = tcollection
    ItemsView = tiv
    List = tlist
    Iterable = titerable
    Union = tunion
    Dict = tdict
    Mapping = tmap
    get_args = tga
    get_origin = tgo
    Type = ttype
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    TypeVar = None
    Callable = None
    Any = None
    Optional = None
    SupportsIndex = None
    Collection = None
    ItemsView = None
    List = None
    Iterable = None
    Union = None
    Dict = None
    Mapping = None
    get_args = notImplemented
    get_origin = notImplemented
    Type = None
