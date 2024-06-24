import copy
import math

import numpy as np

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Clipping import line_clips_rectangle
from Pythoncode.grpc.protobuf_pb2_grpc import Robot
from Pythoncode.model.CourtState import CourtProperty, CourtState
from Pythoncode.model.Rectangle import Rectangle, get_closest_points
from Pythoncode.model.Vector import Vector
from Pythoncode.model.coordinate import Coordinate

CLEARANCE = 2
TURN_DEGREES = 15


def line_collides_with_rectangle(box: Rectangle, begin: Coordinate, to: Coordinate):
    if in_obstacle(box, to):
        return False

    return line_clips_rectangle(box, begin, to)


def robot_collides(box: Rectangle, begin: Coordinate, to: Coordinate, pixel_per_cm: int):
    left_p1, left_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                         VectorUtils.get_vector(begin, to),
                                                                         pixel_per_cm * 10, True)
    right_p1, right_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                           VectorUtils.get_vector(begin, to),
                                                                           pixel_per_cm * 10, False)
    collides = (line_collides_with_rectangle(box, begin, to) or
                line_collides_with_rectangle(box, left_p1, left_p2) or
                line_collides_with_rectangle(box, right_p1, right_p2))

    print("Center hit: " + str(line_collides_with_rectangle(box, begin, to)) + "\n" +
          "Left hit: " + str(line_collides_with_rectangle(box, left_p1, left_p2)) + "\n" +
          "Right hit: " + str(line_collides_with_rectangle(box, right_p1, right_p2)) + "\n")

    return collides


def in_obstacle(box: Rectangle, to: Coordinate):
    return box.c1.x <= to.x <= box.c2.x and box.c1.y <= to.y <= box.c2.y


def turn_robot_internal(robot: Robot, point1: Coordinate, point2: Coordinate) -> float:
    # two points define the line
    normalized_wall = Vector(point1, point2).normalize()
    ap = Vector(robot.center, point1)
    dot_product = ap.get_dot_product(normalized_wall)
    point_on_obstacle = point1.add_vector(normalized_wall.scale(dot_product))  # x is a point on a line
    robot_length = robot.get_centerline_as_vector().length() / 2 + CLEARANCE
    return VectorUtils.get_length(point_on_obstacle, robot.center) - robot_length


def turn_robot(robot: Robot) -> float:
    corner_centers = [corner.center for corner in CourtState.getProperty(CourtProperty.CORNERS)]
    obstacle = CourtState.getProperty(CourtProperty.OBSTACLE)
    corner_point1, corner_point2 = get_closest_points(robot.center, corner_centers)
    obstacle_point1, obstacle_point2 = get_closest_points(robot.center, obstacle.get_corners())
    return max(turn_robot_internal(robot, obstacle_point1, obstacle_point2), turn_robot_internal(robot, corner_point1, corner_point2))
