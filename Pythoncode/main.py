import configparser
from time import sleep

import cv2
import grpc
import numpy

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Collision import in_obstacle
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.Pathfinding.drive_points import *
from Pythoncode.Pathfinding import Pathfinding, DeliverySystem, CornerUtils
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2
from Pythoncode.model import Ball
from Pythoncode.model.Vector import Vector
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
    pathfinding = Pathfinding(balls, robot.center, CourtState.getProperty(CourtProperty.OBSTACLE), pixel_per_cm, drive_points)
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
        while len(pathfinding.targets) > 0 or True:
            robot = CourtState.getProperty(CourtProperty.ROBOT)
            target = pathfinding.get_closest(robot.center)
            drive_function(stub, target, drive_points)
            success = True
            while success:
                try:
                    CourtState.updateObjects(drive_points.drive_points, target)
                    success = False
                except Exception as e:
                    print("Robot not found")
                    sleep(1)

            pathfinding.update_target(CourtState.getProperty(CourtProperty.BALLS))
            
        print("Getting vip")
        target = CourtState.getProperty(CourtProperty.VIP)
        drive_function(stub, target, drive_points)
        stub.Vacuum(protobuf_pb2.VacuumPower(power=False))

        # True implies that ball will be delivered in the goal to the right of the camera
        DeliverySystem.deliver_balls_to_goal(stub, robot, drive_points, drive, True)

def drive_function(stub, target: Ball, drive_points):
    robot = CourtState.getProperty(CourtProperty.ROBOT)

    if target is not None and target.collection_point is not None:
        print("Target collection point not none")
        on_drive_point, coordinate = drive_points.is_on_drive_point(robot.center)
        if on_drive_point:
            if coordinate.x == target.collection_point.x and coordinate.y == target.collection_point.y:
                print("On collection point, moving to target.")
                drive(stub, robot, target.center,True, False)
                return
        target = None


    """This should handle if we cannot see a ball, and move the robot towards the next drive point."""
    if target is None:
        print("Target is None. Moving to drive point...")
        drive(stub, robot, drive_points.get_next_drive_point(robot.center), is_drive_point=True)
        return


    wall_close = False
    corners = CourtState.getProperty(CourtProperty.CORNERS)

    for i in range(len(corners)):
        in_corner = corners[i].is_in_corner(target.center)
        wall_close = target.get_distance_to_wall(corners[i], CornerUtils.get_next(corners[i], corners)) < 50.0
        if in_corner or wall_close:
            drive_point = drive_points.get_next_drive_point(target.center)
            on_drive_point, coordinate = drive_points.is_on_drive_point(robot.center)
            target.collection_point = drive_points.get_closest_drive_point(target.center)
            if on_drive_point:
                if coordinate.x == target.collection_point.x and coordinate.y == target.collection_point.y:
                    print("At drive point. Moving to target")
                    drive(stub, robot, target.center, True)
                    return
                drive(stub, robot, drive_point, is_drive_point=False)
                return

    else:
        print("Going to target...")
        drive_points.last = None
        drive(stub, robot, target.center)




def drive(stub, robot, target, backup=False, is_drive_point=False):
    angle = VectorUtils.calculate_angle_clockwise(target, robot.front, robot.center)
    print("Turning " + str(angle))
    turn = stub.Turn(protobuf_pb2.TurnRequest(degrees=numpy.float32(angle)))
    print("Return value Turn: " + str(turn))
    length_to_target = VectorUtils.get_length(target, robot.front)
    if is_drive_point:
        length_to_target += VectorUtils.get_length(robot.center, robot.front)
    length = int(((length_to_target / pixel_per_cm)-3)*0.99)
    print("Length: " + str(length))
    move = stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=length, speed=70))
    print("Return value Move: " + str(move))
    if backup:
        sleep(2)
        if length > 10:
            length = 10
        print("Backing up " + str(length))
        backed = stub.Move(protobuf_pb2.MoveRequest(direction=False, distance=int(length), speed=50))
        print("Return value Backup: " + str(backed))



if __name__ == '__main__':
    main()
