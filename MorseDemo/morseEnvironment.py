from morse.builder import *

uav = Quadrotor(name="Mein toller Kopter")

##Actuator
motion = MotionVW()
motion.translate()
uav.append(motion)

##Sensor
pose = Pose("pose_Mein toller Kopter")
pose.translate(z=5)
uav.append(pose)

#Waypoint
waypoint = RotorcraftWaypoint("wp_Mein toller Kopter")
uav.append(waypoint)

##Socket um Datenströme abzugreifen
uav.add_default_interface('socket')
pose.add_stream('socket')
pose.add_service('socket')
motion.add_service('socket')
waypoint.add_stream('socket')

env = Environment('outdoors')
env.set_camera_location([5, -5, 6])
env.set_camera_rotation([1.0470, 0, 0.7854])

