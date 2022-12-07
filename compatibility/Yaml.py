from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from compatibility.Typing import Any
    
    from yaml import safe_load as yamlSafeLoad, dump as yamlDump, YAMLError, SafeDumper
    
    yamlError = YAMLError
    dump = yamlDump
    safe_load = yamlSafeLoad
    
    
    def read(file: str) -> dict[str, Any]:
        try:
            with open(file, "r") as stream:
                return safe_load(stream)
        except OSError:
            print("loading yml failed")
            return {}
    
    
    class IgnAliDump(SafeDumper):
        
        def ignore_aliases(self, data):
            return True
    
    
    def write(data: dict[str, Any], file: str):
        with open(file, "w", encoding="utf8") as stream:
            dump(data, stream, default_flow_style=False, allow_unicode=True, Dumper=IgnAliDump)
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    yamlError = None
    dump = notImplemented
    safe_load = notImplemented
    read = notImplemented
    IgnAliDump = None
    write = notImplemented
