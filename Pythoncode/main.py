import configparser
from time import sleep

import cv2
import grpc
import numpy

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Collision import line_hits_rectangle
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.Pathfinding.drive_points import *
from Pythoncode.Pathfinding import Pathfinding, DeliverySystem, CornerUtils
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2
from Pythoncode.model import Ball, Vector
from Pythoncode.model.CourtState import CourtState, CourtProperty

pixel_per_cm = 2.0


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    CourtState.setupCam()

    CourtState.initialize()

    corners = CourtState.getProperty(CourtProperty.CORNERS)
    global pixel_per_cm
    pixel_per_cm = CornerUtils.get_cm_per_pixel(corners, CourtState.getProperty(CourtProperty.BALLS), config)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    """goals = calculate_goals(corners)"""
    balls = CourtState.getProperty(CourtProperty.BALLS)
    drive_points = Drive_points(corners, pixel_per_cm)
    pathfinding = Pathfinding(balls, robot.center, CourtState.getProperty(CourtProperty.OBSTACLE))
    commandHandler(pathfinding, drive_points)


def commandHandler(pathfinding, drive_points):
    config = configparser.ConfigParser()
    config.read('config.ini')
    ip = config.get("ROBOT", "ip")
    CourtState.updateObjects(drive_points.drive_points,None)

    with grpc.insecure_channel(ip) as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        stub.Vacuum(protobuf_pb2.VacuumPower(power=True))
        stub.Vacuum(protobuf_pb2.VacuumPower(power=True))
        robot = CourtState.getProperty(CourtProperty.ROBOT)
        while len(pathfinding.targets) > 0 or True:

            target = pathfinding.get_closest(robot.center)

            drive_function(stub, target, drive_points)
            #sleep(1.5)
            success = True
            while success:
                try:
                    CourtState.updateObjects(drive_points.drive_points,target)
                    success = False
                except Exception as e:
                    print("Robot not found")
                    sleep(1)

            pathfinding.update_target(CourtState.getProperty(CourtProperty.BALLS))
            

        # True implies that ball will be delivered in the goal to the right of the camera
        DeliverySystem.deliver_balls_to_goal(stub, robot, drive_points, drive, True)

def drive_function(stub, target: Ball, drive_points):
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    #sleep(0.5)
    """This should handle if we cannot see a ball, and move the robot towards the next drive point."""
    if target is None:
        print("Target is None. Moving to drive point...")
        drive(stub, robot, drive_points.get_closest_drive_point(robot.center))
        return

    wall_close = False
    corners = CourtState.getProperty(CourtProperty.CORNERS)
    egg = CourtState.getProperty(CourtProperty.EGG)
    egg_close = egg.ball_inside_buffer(target.center)
    print("Testing close to egg. Result = " + str(egg_close))

    for i in range(len(corners)):
        in_corner = corners[i].is_in_corner(target.center)
        wall_close = target.get_distance_to_wall(corners[i], CornerUtils.get_next(corners[i], corners)) < 50.0
        if in_corner or wall_close or egg_close:
            print("Target is in corner. Moving to drive point closest to target.")
            drive_point = drive_points.get_closest_drive_point(target.center)
            if drive_points.is_on_drive_point(robot.center):
                print("At drive point. Moving to target")
                if egg_close:
                    drive(stub, robot, target.center, True, 5)
                else:
                    drive(stub, robot, target.center, True)
                return
            drive(stub, robot, drive_point)
            return


    else:
        drive_points.last = None
        drive(stub, robot, target.center)




def drive(stub, robot, target, backup=False, buffer = 0.0, speed = 90):
    #angle = VectorUtils.calculate_angle_clockwise(target, robot.front, robot.center)
    angle = VectorUtils.calculate_angle_clockwise(target, robot.front, robot.center)
    print("Turning " + str(angle))

    turn = stub.Turn(protobuf_pb2.TurnRequest(degrees=numpy.float32(angle)))
    print("Return value Turn: " + str(turn))
    length = round((((((VectorUtils.get_length(target, robot.center))-(Vector(robot.front, robot.center).length())) / pixel_per_cm)+1)*0.92), 3) - buffer
    print("Length: " + str(int(length)))

    if backup:
        print("Going slow")
        move = stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=30))
        print("Return value Move: " + str(move))
        sleep(1)
        print("Backing up "+str(length))
        backed = stub.Move(protobuf_pb2.MoveRequest(direction=False, distance=int(length), speed=speed))
        print("Return value Backup: " + str(backed))
    else:
        print("Speedy")
        move = stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=speed))
        print("Return value Move: " + str(move))


if __name__ == '__main__':
    main()
