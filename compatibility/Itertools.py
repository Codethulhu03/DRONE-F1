from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from itertools import product as iterProd, chain as iterChain, combinations as iterComb, permutations as iterPerm
    
    product = iterProd
    chain = iterChain
    combinations = iterComb
    permutations = iterPerm
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    product = notImplemented
    chain = notImplemented
    combinations = notImplemented
    permutations = notImplemented
