import configparser

import grpc
from ultralytics import YOLO
import cv2

from Pythoncode.Pathfinding import VectorUtils, CornerUtils
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.grpc.protobuf_pb2_grpc import Robot
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner
from Pythoncode.model.CourtState import CourtState, CourtProperty

from Pythoncode.grpc.gRPC_Class import gRPC_Class
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Robot import Robot
from Pythoncode.model.Vip import Vip
from Pythoncode.model.CourtState import CourtState, CourtProperty

from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2

from Pythoncode.Pathfinding.CornerUtils import set_placements, calculate_goals

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
            target = pathfinding.get_closest(robot.center)
            drive_function(stub, target)

            CourtState.updateObjects()
            pathfinding.update_target(CourtState.getProperty(CourtProperty.BALLS))
            cv2.waitKey(1500)
        print("Getting vip")
        target = CourtState.getProperty(CourtProperty.VIP)
        drive_function(stub, target)

def drive_function(stub, target):
    robot = CourtState.getProperty(CourtProperty.ROBOT)

    angle = VectorUtils.calculate_angle_clockwise(target.center, robot.front, robot.center)

    cv2.waitKey(1500)
    angle = round(angle, 3)

    stub.Turn(protobuf_pb2.TurnRequest(degrees=angle))
    length = round(VectorUtils.get_length(target.center, robot.front) / pixel_per_cm) * 0.9

    cv2.waitKey(1500)
    stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=70))
    cv2.waitKey(1500)


if __name__ == '__main__':
    main()
