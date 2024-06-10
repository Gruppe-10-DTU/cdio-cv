import configparser

import grpc
from ultralytics import YOLO
import cv2

from Pythoncode.Pathfinding import VectorUtils, CornerUtils
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.model.CourtState import CourtState, CourtProperty

from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2

from Pythoncode.Pathfinding.CornerUtils import set_placements, calculate_goals



pixel_per_cm = 2.0
def main():
    """
    model = YOLO("model/best.pt")
    # cap = cv2.VideoCapture('videos/with_egg.mp4')
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    CourtState.addProperties(model, cap)
    """
    CourtState.initialize()

    corners = CourtState.getProperty(CourtProperty.CORNERS)
    corners = set_placements(corners)
    global pixel_per_cm
    pixel_per_cm = CornerUtils.get_cm_per_pixel(corners)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    CourtState.startThread()
    """goals = calculate_goals(corners)"""
    balls = CourtState.getProperty(CourtProperty.BALLS)
    pathfinding = Pathfinding(balls, robot.center)
    commandHandler(pathfinding)


def commandHandler(pathfinding):
    config = configparser.ConfigParser()
    config.read('config.ini')
    ip = config.get("ROBOT", "ip")
    with grpc.insecure_channel(ip) as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)

        while len(pathfinding.targets) > 0:
            robot = CourtState.getProperty(CourtProperty.ROBOT)
            target = pathfinding.get_closest(robot.center)
            cv2.waitKey(1500)

            angle = VectorUtils.calculate_angle_clockwise(target.center, robot.front, robot.center)
            angle = round(angle)
            if angle > 180:
                angle -= 360
            cv2.waitKey(1500)

            stub.Turn(protobuf_pb2.TurnRequest(degrees=angle))
            length = round(VectorUtils.get_length(target.center, robot.front) / pixel_per_cm)*0.9

            stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=70))
            cv2.waitKey(15000)

            pathfinding.remove_target(target)




if __name__ == '__main__':
    main()
