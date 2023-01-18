from compatibility.Sys import sys, stdout  # sys for sys.stdout, stdout for saved stdout reference


class HiddenPrints:
    """
    Class to hide prints from the console.
    
    .. note:: Logging will still work, only explicit print() calls will be hidden, which shouldn't be used anyway.
    -> Use this for hiding Library prints. (ContextManager - *with HiddenPrints():*)
    """
    
    def __enter__(self):
        """ Redirects stdout to None """
        sys.stdout = None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Restores stdout """
        sys.stdout = stdout
