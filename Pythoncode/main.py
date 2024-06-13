import configparser
import math

import grpc
from ultralytics import YOLO
import cv2

from Pythoncode.Pathfinding import VectorUtils, CornerUtils
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from time import sleep
from Pythoncode.grpc.protobuf_pb2_grpc import Robot
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner
from Pythoncode.model.CourtState import CourtState, CourtProperty

from Pythoncode.grpc.gRPC_Class import gRPC_Class
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Robot import Robot
from Pythoncode.model.Vip import Vip
from Pythoncode.model.Ball import Ball
from Pythoncode.model.CourtState import CourtState, CourtProperty

from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2

from Pythoncode.Pathfinding.CornerUtils import set_placements, calculate_goals

from Pythoncode.Pathfinding.drive_points import *

import Pythoncode.model
from Pythoncode.model.coordinate import Coordinate


pixel_per_cm = 2.0
def main():

    CourtState.initialize()

    corners = CourtState.getProperty(CourtProperty.CORNERS)
    corners = set_placements(corners)
    global pixel_per_cm
    pixel_per_cm = CornerUtils.get_cm_per_pixel(corners)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    """goals = calculate_goals(corners)"""
    balls = CourtState.getProperty(CourtProperty.BALLS)
    pathfinding = Pathfinding(balls, robot.center)

    commandHandler(pathfinding)


def commandHandler(pathfinding):
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
            drive_function(stub, target)
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

def drive_function(stub, target):
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    corner = False
    cv2.waitKey(500)
    """Almost positive this is a stupid solution."""
    for corner in CourtState.getProperty(CourtProperty.CORNERS):
        corner = target.is_in_corner(corner)
    if target.is_in_corner(corner):
        print("Target is in corner. Moving to drive point closest to target.")
        tmp_target = Pythoncode.Pathfinding.Pathfinding.drive_points.get_closest_drive_point(target)
        tmp_angle = VectorUtils.calculate_angle_clockwise(tmp_target, robot.front, robot.center)
        print("Turning" + str(tmp_angle))
        stub.Turn(protobuf_pb2.TurnRequest(degrees=tmp_angle))
        tmp_length = round(VectorUtils.get_length(tmp_target, robot.front)/pixel_per_cm*0.9)
        print("Length: " + str(tmp_length))
        stub.MoveRequest(protobuf_pb2.MoveRequest(direction=True,distance=int(tmp_length),speed=70))

        cv2.waitKey(500)
        angle = VectorUtils.calculate_angle_clockwise(target.center, robot.front, robot.center)
        angle = round(angle, 3)
        print("Turning " + str(angle))
        stub.Turn(protobuf_pb2.TurnRequest(degrees=angle))
        length = round(VectorUtils.get_length(target.center, robot.front) / pixel_per_cm) * 0.9
        print("Length: " + str(length))
        cv2.waitKey(500)
        stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=70))
        stub.Move(protobuf_pb2.MoveRequest(direction=False,distance=int(length), speed=50))
    else:
        cv2.waitKey(500)
        angle = VectorUtils.calculate_angle_clockwise(target.center, robot.front, robot.center)
        angle = round(angle, 3)
        print("Turning " + str(angle))
        stub.Turn(protobuf_pb2.TurnRequest(degrees=angle))
        length = round(VectorUtils.get_length(target.center, robot.front) / pixel_per_cm) * 0.9
        print("Length: " + str(length))
        cv2.waitKey(500)
        stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=70))


if __name__ == '__main__':
    main()
