import math

import numpy as np

from Pythoncode.model.Vector import Vector
from Pythoncode.model.coordinate import Coordinate


def get_length(point1: Coordinate, point2: Coordinate) -> float:
    return math.sqrt(math.pow(point2.x - point1.x, 2) + math.pow(point2.y - point1.y, 2))


def get_vector(coordinate1: Coordinate, coordinate2: Coordinate) -> Vector:
    return Vector(coordinate2.x - coordinate1.x, coordinate2.y - coordinate1.y)


def get_vector_length(vector: Vector) -> float:
    length = math.sqrt(math.pow(vector.x, 2) + math.pow(vector.y, 2))
    return length


def calculate_angle_clockwise(target: Coordinate, robot_front: Coordinate, center: Coordinate) -> float:
    vector2 = get_vector(center, target)
    vector1 = get_vector(center, robot_front)
    #vector1 = vector1.normalize()
    #vector2 = vector2.normalize()
    dotproduct = (vector1.x * vector2.x + vector1.y * vector2.y)
    other = vector2.y * vector1.x - vector2.x * vector1.y
    arctan2 = math.degrees(math.atan2(other, dotproduct))
    return round(arctan2, 3)

