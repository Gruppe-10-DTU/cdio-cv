import configparser

import cv2
import grpc
import pathfinding
from pandas.conftest import ip

from Pythoncode.main import drive_function, pixel_per_cm
from Pythoncode.model.coordinate import Coordinate
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
from Pythoncode.model.CourtState import CourtState, CourtProperty
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2
from Pythoncode.Pathfinding.CornerUtils import set_placements, calculate_goals
from Pythoncode.main import drive_function
from Pythoncode.main import commandHandler
from Pythoncode.grpc.protobuf_pb2_grpc import Robot
from Pythoncode.Pathfinding.VectorUtils import calculate_path

config = configparser.ConfigParser()
config.read('../config.ini')
ip = config.get("ROBOT", "ip")
with grpc.insecure_channel(ip) as channel:
    stub = protobuf_pb2_grpc.RobotStub(channel)
    stub.StopMovement(protobuf_pb2.Empty())
    stub.Vacuum(protobuf_pb2.VacuumPower(power=True))
    stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=30, speed=60))
    stub.Move(protobuf_pb2.MoveRequest(direction=False, distance=30, speed=60))
    stub.Vacuum(protobuf_pb2.VacuumPower(power=False))


# 	1.	Navigate to the Delivery Point: Use pathfinding and vector utilities to move the robot to the delivery point.
##  We need to determine the path from the current position to the delivery point. This involves a simple straight line
##  if there are no obstacles and a more complex path when there are obstacles.

# 	2.	Align the Mouthpiece: Adjust the robot’s orientation to align the mouthpiece with the delivery point’s opening.
# 	3.	Turn off the Motor: Stop the motor to release the balls once aligned.

#   1.	Path Calculation: Determine the path from the robot’s current position to the delivery point.
# 	2.	Movement Execution: Move the robot along the calculated path.
# 	3.	Alignment: Adjust the robot’s orientation to align with the delivery point.
# 	4.	Delivery: Perform the action to deliver the balls

def deliver_balls_to_goal(robot: RobotStub, delivery_point: Coordinate, motor_control):
    current_position = robot.get_current_position()  # Assuming this method exists
    path = calculate_path(current_position, delivery_point)

    for driving_point in path:
        drive_function(robot, driving_point)

    alignment_successful = align_robot_with_delivery_point(robot, delivery_point)
    if alignment_successful:
        # 3: Turn off the motor to release balls (done)


        stub.Vacuum(False)
        print("Balls delivered successfully!")
    else:
        # Failed to align. Print error msg
        print("Alignment failed. Cannot deliver balls.")


def align_robot_with_delivery_point(robot: RobotStub, delivery_point: Coordinate) -> bool:

    current_position = robot.get_current_position()  # if this method doesn't exist, it needs to be created
    robot_front = robot.get_front_position()  # if this method doesn't exist, it needs to be created
    angle = calculate_angle_clockwise(delivery_point, robot_front, current_position)

    if angle != 0:
        robot.Turn(protobuf_pb2.TurnRequest(degrees=angle))
        sleep(1)  # Wait for the robot to complete the turn

    # Assuming the robot has a method to check its current angle
    # and we compare it with the expected angle to determine if alignment is correct.
    current_angle = robot.get_current_angle()  # Assuming this method exists
    expected_angle = calculate_angle_clockwise(delivery_point, robot.get_front_position(), robot.get_current_position())

    return abs(current_angle - expected_angle) < tolerance  # tolerance is a small value like 1 degree


def drive_function(robot: RobotStub, target: Coordinate):
    current_position = robot.get_current_position()  # # if this method doesn't exist, it needs to be created
    distance = get_length(current_position, target)
    robot.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(distance), speed=70))
    sleep(1)  # Wait for the robot to complete the move


