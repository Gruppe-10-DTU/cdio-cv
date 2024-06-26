import copy
import math

import numpy as np
from numpy.linalg import norm

from Pythoncode.Pathfinding import VectorUtils, CornerUtils
from Pythoncode.Pathfinding.Clipping import line_clips_rectangle
from Pythoncode.grpc.protobuf_pb2_grpc import Robot
from Pythoncode.model.CourtState import CourtProperty, CourtState
from Pythoncode.model.Rectangle import Rectangle, get_closest_points
from Pythoncode.model.Vector import Vector
from Pythoncode.model.coordinate import Coordinate

CLEARANCE = 1.5
TURN_DEGREES = 15


def line_collides_with_rectangle(box: Rectangle, begin: Coordinate, to: Coordinate):
    if in_obstacle(box, to):
        return False

    return line_clips_rectangle(box, begin, to)


def robot_collides(box: Rectangle, begin: Coordinate, to: Coordinate, pixel_per_cm: float):
    left_p1, left_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                         VectorUtils.get_vector(begin, to),
                                                                         pixel_per_cm * 10, True)
    right_p1, right_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                           VectorUtils.get_vector(begin, to),
                                                                           pixel_per_cm * 10, False)
    collides = (line_collides_with_rectangle(box, begin, to) or
                line_collides_with_rectangle(box, left_p1, left_p2) or
                line_collides_with_rectangle(box, right_p1, right_p2))

    return collides


def in_obstacle(box: Rectangle, to: Coordinate):
    return box.c1.x <= to.x <= box.c2.x and box.c1.y <= to.y <= box.c2.y


def turn_robot_internal(turning_point: Coordinate, robot_length: float, point1: Coordinate, point2: Coordinate) -> float:
    # two points define the line
    p1 = np.array([point1.x, point1.y])
    p2 = np.array([point2.x, point2.y])
    p3 = np.array([turning_point.x, turning_point.y])

    # x is a point on a line
    robot_radius = robot_length * CLEARANCE
    ball_position = np.abs(norm(np.cross(p2-p1, p1-p3))) / norm(p2-p1)
    difference = ball_position - robot_radius
    return difference


def turn_robot(point: Coordinate, robot_length: float) -> float:
    corners = CourtState.getProperty(CourtProperty.CORNERS)
    close_items = []

    for corner in corners:
        next_corner = CornerUtils.get_next(corner, corners)
        length = turn_robot_internal(point, robot_length, corner.center, next_corner.center)
        if turn_robot_internal(point, robot_length, corner.center, next_corner.center) < 0:
            close_items.append(length)

    obstacle = CourtState.getProperty(CourtProperty.OBSTACLE)
    obstacle_point1, obstacle_point2 = get_closest_points(point, obstacle.get_corners())
    length = turn_robot_internal(point, robot_length, obstacle_point1, obstacle_point2)
    close_items.append(length)

    return min(close_items)
