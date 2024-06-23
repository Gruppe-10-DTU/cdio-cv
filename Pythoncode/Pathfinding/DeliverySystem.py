from time import sleep

from Pythoncode.model.coordinate import Coordinate
from Pythoncode.Pathfinding import VectorUtils, Collision
from Pythoncode.Pathfinding.drive_points import WALL_DISTANCE
from Pythoncode.model.CourtState import CourtState, CourtProperty
from Pythoncode.model.Vector import Vector
from Pythoncode.grpc import protobuf_pb2


def deliver_balls_to_goal(rpc, robot, drive_points, drive, big_goal=True):
    obstacle = CourtState.getProperty(CourtProperty.OBSTACLE)
    target_drive_point_index = 3 if big_goal else 7
    target_drive_point = drive_points.get_drive_points()[target_drive_point_index]
    # Drive to the target drive point
    while Collision.p_clips(obstacle, robot.center, target_drive_point,
                            CourtState.getProperty(CourtProperty.PIXEL_PER_CM)):
        CourtState.updateObjects(drive_points.drive_points, target_drive_point)
        robot = CourtState.getProperty(CourtProperty.ROBOT)
        route_point = drive_points.get_next_drive_point(robot.center)
        # Move using the supplied drive function (it the one from main)
        drive(rpc, robot, route_point, is_drive_point=True)
        # Not sure if this is needed
    CourtState.updateObjects(drive_points.drive_points, target_drive_point)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    drive(rpc, robot, target_drive_point, is_drive_point=True)
    delivery_point = calculate_delivery_point(robot, target_drive_point, drive_points, big_goal)
    alignment_point = calculate_alignment_point(target_drive_point, delivery_point)
    alignment_successful = align_robot_with_delivery_point(robot, alignment_point, delivery_point, rpc)
    if alignment_successful:
        # 3: Turn off the motor to release balls (done)
        rpc.Vacuum(protobuf_pb2.VacuumPower(power=False))
        #sleep(0.5)
        #rpc.Move(protobuf_pb2.MoveRequest(direction=True,distance=1,speed=30))

        print("Balls delivered successfully!")
    else:
        # Failed to align. need to implement realignment
        print("Alignment failed. Cannot deliver balls.")


def align_robot_with_delivery_point(robot, drive_point: Coordinate, delivery_point: Coordinate, rpc) -> bool:
    CourtState.updateObjects([delivery_point, drive_point], drive_point)
    robot = CourtState.getProperty(CourtProperty.ROBOT)
    while VectorUtils.get_length(robot.center, drive_point) > 2.0 * CourtState.getProperty(CourtProperty.PIXEL_PER_CM):
        angle = VectorUtils.calculate_angle_clockwise(drive_point, robot.front, robot.center)
        move_direction = True
        # turn opposite and reverse if it is shorter
        if angle > 90:
            angle = angle - 180
            move_direction = False
        elif angle < -90:
            angle = angle + 180
            move_direction = False
        # Slowly turn the robot and move it to the drive point
        rpc.Turn(protobuf_pb2.TurnRequest(degrees=angle, speed=50))
        offset = VectorUtils.get_length(robot.center, drive_point) / CourtState.getProperty(CourtProperty.PIXEL_PER_CM)
        rpc.Move(protobuf_pb2.MoveRequest(direction=move_direction, distance=int(offset), speed=35))
        CourtState.updateObjects([delivery_point, drive_point], drive_point)
        robot = CourtState.getProperty(CourtProperty.ROBOT)
    # point the robot to the delivery point
    delivery_distance = VectorUtils.get_length(robot.front, delivery_point) / CourtState.getProperty(
        CourtProperty.PIXEL_PER_CM)  # - 1 * CourtState.getProperty(CourtProperty.PIXEL_PER_CM)
    while delivery_distance > 3:
        angle = VectorUtils.calculate_angle_clockwise(delivery_point, robot.front, robot.center)
        if angle > 2 or angle < -2:
            rpc.Turn(protobuf_pb2.TurnRequest(degrees=angle, speed=50))
        # Move the robot to the delivery point
        CourtState.updateObjects([delivery_point, drive_point], drive_point)
        robot = CourtState.getProperty(CourtProperty.ROBOT)
        delivery_distance = ((VectorUtils.get_length(robot.front, delivery_point) / CourtState.getProperty(
            CourtProperty.PIXEL_PER_CM)) - 5)
        rpc.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(delivery_distance/2), speed=30))
        CourtState.updateObjects([delivery_point, drive_point], drive_point)
        robot = CourtState.getProperty(CourtProperty.ROBOT)
        delivery_distance = ((VectorUtils.get_length(robot.front, delivery_point) / CourtState.getProperty(
            CourtProperty.PIXEL_PER_CM)) - 5)
    offset = VectorUtils.get_length(robot.front, delivery_point) / CourtState.getProperty(CourtProperty.PIXEL_PER_CM) - 5
    return offset < 5.0


def calculate_delivery_point(robot, alignment_point, drive_points, big_goal):
    helper_index = 2 if big_goal else 6
    # Requires checking that the orthogonal is returned in the right direction
    # otherwise just invert it
    helper_vector = (Vector(alignment_point, drive_points.get_drive_points()[helper_index]).orthogonal().invert()
                     .scale_to_length(WALL_DISTANCE * CourtState.getProperty(CourtProperty.PIXEL_PER_CM)))
    goal_point = alignment_point.add_vector(helper_vector)
    # drive_vector = Vector(alignment_point, goal_point)
    # delivery_point = alignment_point.add_vector(drive_vector)
    return goal_point  # delivery_point


# Simply moved the point the robot lines up at a bit closer to the wall
# to reduce driving distance
def calculate_alignment_point(drive_point, delivery_point):
    alignment_vector = Vector(drive_point, delivery_point).scale_to_length(
        5 * CourtState.getProperty(CourtProperty.PIXEL_PER_CM))
    return drive_point.add_vector(alignment_vector)
