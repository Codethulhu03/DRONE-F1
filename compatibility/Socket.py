from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from socket import (socket as sock, AF_INET as inet, SO_BROADCAST as bc, SOL_SOCKET as sol, SOCK_DGRAM as dgram,
                        gethostname as sockgethost, SHUT_RDWR as shut)
    
    socket = sock
    gethostname = sockgethost
    AF_INET = inet
    SO_BROADCAST = bc
    SOL_SOCKET = sol
    SOCK_DGRAM = dgram
    SHUT_RDWR = shut
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    socket = None
    gethostname = notImplemented
    AF_INET = None
    SO_BROADCAST = None
    SOL_SOCKET = None
    SOCK_DGRAM = None
