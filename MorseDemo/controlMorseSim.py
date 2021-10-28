from typing import get_type_hints
from pymorse import Morse

morseSim = Morse()

for drone in morseSim.robots:
    uav = getattr(morseSim, drone)
    wp = getattr(uav, "wp_Mein toller Kopter")
    pose = getattr(uav, "pose_Mein toller Kopter")
    
wp.publish({'x': 5, 'y':10, 'z':  10, 'yaw': 0, 'tolerance': 1, 'linVelocityMax':2})

def printDaten(data):
    print(data)
pose.subscribe(printDaten)

input()
    
    