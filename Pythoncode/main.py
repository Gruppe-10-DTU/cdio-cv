import configparser
import math
from time import sleep

import grpc
import numpy

from Pythoncode.Pathfinding import Pathfinding, DeliverySystem
from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Collision import turn_robot
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.Pathfinding.drive_points import *
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2
from Pythoncode.model import Ball
from Pythoncode.model.CourtState import CourtState, CourtProperty


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    CourtState.setupCam()

    CourtState.initialize()

    corners = CourtState.getProperty(CourtProperty.CORNERS)

    scale = CornerUtils.get_cm_per_pixel(corners, CourtState.getProperty(CourtProperty.BALLS), config)
    CourtState.set_property(CourtProperty.PIXEL_PER_CM, scale)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    balls = CourtState.getProperty(CourtProperty.BALLS)
    drive_points = Drive_points(corners, CourtState.getProperty(CourtProperty.PIXEL_PER_CM))
    pathfinding = Pathfinding(balls, robot.center, CourtState.getProperty(CourtProperty.OBSTACLE), CourtState.getProperty(CourtProperty.PIXEL_PER_CM), drive_points)
    commandHandler(pathfinding, drive_points)


def commandHandler(pathfinding, drive_points):
    config = configparser.ConfigParser()
    config.read('config.ini')
    ip = config.get("ROBOT", "ip")
    while True:
        try:
            CourtState.updateObjects(drive_points.drive_points,None)
            with grpc.insecure_channel(ip) as channel:
                stub = protobuf_pb2_grpc.RobotStub(channel)
                stub.Vacuum(protobuf_pb2.VacuumPower(power=True))
                while len(pathfinding.targets) > 0:
                    egg = CourtState.getProperty(CourtProperty.EGG)
                    robot = CourtState.getProperty(CourtProperty.ROBOT)
                    target = pathfinding.get_closest(robot.center, egg)
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
                CourtState.updateObjects(None, None)
                robot = CourtState.getProperty(CourtProperty.ROBOT)
                # True implies that ball will be delivered in the goal to the right of the camera
                DeliverySystem.deliver_balls_to_goal(stub, robot, drive_points, drive, False)
                """"Hacky fix"""
                break
        except Exception as e:
            print(str(e))
            print("Robot died. Sleeping for 5")
            sleep(2)


def drive_function(stub, target: Ball, drive_points):
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    egg = CourtState.getProperty(CourtProperty.EGG)

    if target is not None and target.collection_point is not None:
        print("Target collection point not none")
        on_drive_point, coordinate = drive_points.is_on_drive_point(robot.center)
        if on_drive_point:
            if coordinate.x == target.collection_point.x and coordinate.y == target.collection_point.y:
                if egg.ball_inside_buffer(target.center):
                    drive(stub, robot, target.center, backup=True, is_drive_point=False, buffer = 5)
                else:
                    drive(stub, robot, target.center, backup=True, is_drive_point=False, buffer=3)
                return
        print("Drive to collection point")
        drive(stub, robot, target.collection_point, is_drive_point=True)
        return


    """This should handle if we cannot see a ball, and move the robot towards the next drive point."""
    if target is None:
        print("Target is None. Moving to drive point...")
        drive(stub, robot, drive_points.get_next_drive_point(robot.center), is_drive_point=True)
        return

    corners = CourtState.getProperty(CourtProperty.CORNERS)


    for i in range(len(corners)):
        in_corner = corners[i].is_in_corner(target.center)
        wall_close = target.get_distance_to_wall(corners[i], CornerUtils.get_next(corners[i], corners)) < 50.0
        if in_corner or wall_close:
            drive_point = drive_points.get_closest_drive_point(target.center)
            on_drive_point, coordinate = drive_points.is_on_drive_point(robot.center)
            target.collection_point = drive_points.get_closest_drive_point(target.center)
            if on_drive_point:
                if coordinate.x == target.collection_point.x and coordinate.y == target.collection_point.y:
                    print("At drive point. Moving to target")
                    drive(stub, robot, target.center, backup=True)
                    return
                else:
                    drive(stub, robot, drive_points.get_next_drive_point(target.center), is_drive_point=True)
                return

    print("Going to target...")
    drive_points.last = None
    drive(stub, robot, target.center, buffer=5)




def drive(stub, robot, target, backup=False, buffer = 0.0, speed = 90, is_drive_point=False):
    if backup:
        length_to_target = VectorUtils.get_length(target, robot.center)
        if not is_drive_point:
            length_to_target -= VectorUtils.get_length(robot.center, robot.front)
        length = float(((length_to_target / CourtState.getProperty(CourtProperty.PIXEL_PER_CM)) * 0.5))
        angle = VectorUtils.calculate_angle_clockwise(target, robot.front, robot.center)
        length = math.floor(length)
        print("Turning " + str(angle))

        turn = stub.Turn(protobuf_pb2.TurnRequest(degrees=numpy.float32(angle)))
        move = stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=speed))

        CourtState.updateObjects(None, None)
        robot = CourtState.getProperty(CourtProperty.ROBOT)

    angle = VectorUtils.calculate_angle_clockwise(target, robot.front, robot.center)
    print("Turning " + str(angle))

    turn = stub.Turn(protobuf_pb2.TurnRequest(degrees=numpy.float32(angle)))
    """"DO NOT CHANGE THIS. 
    We calculate angle from center and turn then drive the value of this subtracted from the center.
    This is necessary, or we overshoot if the angle between front and ball is too large.
    """
    print("Return value Turn: " + str(turn))
    CourtState.updateObjects(None, None)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    length_to_target = VectorUtils.get_length(target, robot.center)
    if not is_drive_point:
        length_to_target -= VectorUtils.get_length(robot.center, robot.front)
    print("length to target: "+ str(length_to_target))
    length = (length_to_target / CourtState.getProperty(CourtProperty.PIXEL_PER_CM))
    if length > buffer:
        length = length - buffer
    if length > 4:
        length = length-3
    length = math.floor(length)
    print("Length: " + str(length))

    move = stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length), speed=speed))

    print("Return value Move: " + str(move))
    if backup or turn_robot(target, VectorUtils.get_length(robot.center, robot.front)) < 0:
    #if backup:
        sleep(2)
        if length > 20:
            length = 20
        print("Backing up "+str(length))
        backed = stub.Move(protobuf_pb2.MoveRequest(direction=False, distance=int(length), speed=speed))
        print("Return value Backup: " + str(backed))




if __name__ == '__main__':
    main()
