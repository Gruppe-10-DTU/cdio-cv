import copy
import math

import numpy as np

from Pythoncode.Pathfinding import VectorUtils, CornerUtils
from Pythoncode.model.CourtState import CourtProperty, CourtState
from Pythoncode.model.Vector import Vector
from Pythoncode.model.Corner import Corner

from Pythoncode.model.Rectangle import Rectangle, get_closest_points
from Pythoncode.model.Robot import Robot
from Pythoncode.model.coordinate import Coordinate

"""
This is an implementation of the Cohen-Sutherland algorithm for line clipping
If a line is clipped to fit the rectangle, a collision is detected.
"""

LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8

CLEARANCE = 2
TURN_DEGREES = 15


def calculate_endpoint_outcode(box: Rectangle, coordinate: Coordinate):
    outcode = 0

    if coordinate.x < box.c1.x:
        outcode |= LEFT
    elif coordinate.x > box.c2.x:
        outcode |= RIGHT

    if coordinate.y < box.c1.y:
        outcode |= BOTTOM
    elif coordinate.y > box.c2.y:
        outcode |= TOP

    return outcode


def line_hits_rectangle(box: Rectangle, begin: Coordinate, to: Coordinate):
    if box.c1.x <= to.x <= box.c2.x and box.c1.y <= to.y <= box.c2.y:
        return False

    c1 = copy.deepcopy(begin)
    c2 = copy.deepcopy(to)

    start = calculate_endpoint_outcode(box, c1)
    end = calculate_endpoint_outcode(box, c2)

    does_clip = False
    run = True

    while run:
        if not (start | end):
            does_clip = True
            run = False
        elif start & end:
            run = False
        else:
            outside = start if start > end else end
            x = 0
            y = 0

            if outside & TOP:
                x = c1.x + (c2.x - c1.x) * (box.c2.y - c1.y) / (c2.y - c1.y)
                y = box.c2.y
            elif outside & BOTTOM:
                x = c1.x + (c2.x - c1.x) * (box.c1.y - c1.y) / (c2.y - c1.y)
                y = box.c1.y
            elif outside & LEFT:
                y = c1.y + (c2.y - c1.y) * (box.c1.x - c1.x) / (c2.x - c1.x)
                x = box.c1.x
            elif outside & RIGHT:
                y = c1.y + (c2.y - c1.y) * (box.c2.x - c1.x) / (c2.x - c1.x)
                x = box.c2.x

            if outside == start:
                c1.x = x
                c1.y = y
                start = calculate_endpoint_outcode(box, c1)
            else:
                c2.x = x
                c2.y = y
                end = calculate_endpoint_outcode(box, c2)

    return does_clip


def turn_robot(robot: Robot, angle, point1: Coordinate, point2: Coordinate) -> bool:
    # two points define the line
    normalized_wall = Vector(point1, point2).normalize()
    ap = Vector(robot.center, point1)
    dot_product = ap.get_dot_product(normalized_wall)
    point_on_obstacle = point1.add_vector(normalized_wall.scale(dot_product))  # x is a point on line
    robot_length = robot.get_centerline_as_vector().length() + CLEARANCE
    if VectorUtils.get_length(point_on_obstacle, robot.center) > robot_length:
        return True
    return False


def turn_robot(robot: Robot, angle, obstacle: Rectangle) -> bool:
    point1, point2 = get_closest_points(robot.center, [obstacle.c1, obstacle.c4, obstacle.c2, obstacle.c3])
    return turn_robot(robot, angle, point1, point2)


def turn_robot(robot: Robot, angle) -> bool:
    corner_centers = [corner.center for corner in CourtState.getProperty(CourtProperty.CORNERS)]
    point1, point2 = get_closest_points(robot.center, corner_centers)
    return turn_robot(robot, angle, point1, point2)
