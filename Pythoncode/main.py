import configparser
from time import sleep

import cv2
import grpc

import Pythoncode.model
from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.Pathfinding.drive_points import *
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2
from Pythoncode.model.Ball import Ball
from Pythoncode.model.CourtState import CourtState, CourtProperty

pixel_per_cm = 2.0


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    CourtState.setupCam()

    CourtState.initialize()

    corners = CourtState.getProperty(CourtProperty.CORNERS)
    global pixel_per_cm
    pixel_per_cm = CornerUtils.get_cm_per_pixel(corners, config)
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
    CourtState.updateObjects()

    with grpc.insecure_channel(ip) as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        robot = CourtState.getProperty(CourtProperty.ROBOT)
        while len(pathfinding.targets) > 0:
            success = True
            target = pathfinding.get_closest(robot.center)

            drive_function(stub, target, drive_points)
            sleep(1.5)
            while success:
                try:
                    CourtState.updateObjects()
                    success = False
                except Exception as e:
                    print("Robot not found")
                    sleep(1)

            pathfinding.update_target(CourtState.getProperty(CourtProperty.BALLS))

        print("Getting vip")
        target = CourtState.getProperty(CourtProperty.VIP)
        drive_function(stub, target)


def drive_function(stub, target: Ball, drive_points):
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    cv2.waitKey(500)
    """This should handle if we cannot see a ball, and move the robot towards the next drive point."""
    if target is None:
        print("Target is None. Moving to drive point...")
        drive(stub, drive_points.get_closest_drive_point(robot.center), robot)
        return

    in_corner = False
    wall_close = False
    corners = CourtState.getProperty(CourtProperty.CORNERS)

    for i in range(len(corners)):
        in_corner = corners[i].is_in_corner(target.center)
        wall_close = target.get_distance_to_wall(corners[i], CornerUtils.get_next(corners[i], corners)) < 6.0
        if in_corner or wall_close:
            print("Target is in corner. Moving to drive point closest to target.")
            drive(stub, robot, drive_points.get_closest_drive_point(target.center))

            print("At drive point. Moving to target")
            drive(stub, robot, target.center, True)
            return
    else:
        drive(stub, robot, target.center)
        cv2.waitKey(500)



def drive(stub, robot, target, backup=False):
    angle = VectorUtils.calculate_angle_clockwise(target, robot.front, robot.center)

    print("Turning " + str(angle))
    stub.Turn(protobuf_pb2.TurnRequest(degrees=angle))
    length = round(VectorUtils.get_length(target, robot.front) / pixel_per_cm) * 0.9
    print("Length: " + str(length))
    cv2.waitKey(500)
    stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=70))

    if backup:
        print("Backing up "+str(length))
        stub.Move(protobuf_pb2.MoveRequest(direction=False, distance=int(length), speed=70))


if __name__ == '__main__':
    main()
