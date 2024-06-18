import configparser
from time import sleep

import cv2
import grpc

import Pythoncode.model
from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.Pathfinding.drive_points import *
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2
from Pythoncode.main import drive
from Pythoncode.model.Ball import Ball
from Pythoncode.model.CourtState import CourtState, CourtProperty


def drive_corners():
    config = configparser.ConfigParser()


    config.read('config.ini')
    CourtState.setupCam()

    CourtState.initialize()

    corners = CourtState.getProperty(CourtProperty.CORNERS)

    pixel_per_cm = CornerUtils.get_cm_per_pixel(corners, config)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    """goals = calculate_goals(corners)"""
    drive_points = Drive_points(corners, pixel_per_cm)
    ip = config.get("ROBOT", "ip")

    with grpc.insecure_channel(ip) as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        while True:
            robot = CourtState.getProperty(CourtProperty.ROBOT)
            drive_point = drive_points.get_closest_drive_point(robot.center)
            drive(stub, robot, drive_point)

            sleep(1.5)
            while success:
                try:
                    CourtState.updateObjects()
                    success = False
                except Exception as e:
                    print("Robot not found")
                    sleep(1)


if __name__ == '__main__':
    drive_corners()