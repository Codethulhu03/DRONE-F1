from rplidar import RPLidar
lidar = RPLidar('/dev/ttyUSB0')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

for distance in enumerate(lidar.iter_measurments()):
        print(distance)

lidar.stop()
lidar.stop_motor()
lidar.disconnect()