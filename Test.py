from ThymioSimPG import *
from world import *


point1 = Point(0,0)
point2 = Point(500,500)
point3 = Point(20,20)
point4 = Point(200,300)

floor1 = Floor(point1, point2,(255,0,0))
wall1 = Wall(point3, point4)

world = PGWorld([floor1, wall1])

robot = ThymioSimPG(world)
# robot.robot.setheading(-160)
robot.wheels(500,0)
robot.sleep(5)
print(robot.get_prox_horizontal())
robot.wheels(500,0)
robot.sleep(5)
print("starting to go straight")
robot.wheels(100, 100)
robot.sleep(1)
print(robot.get_prox_ground().delta)

robot.quit()