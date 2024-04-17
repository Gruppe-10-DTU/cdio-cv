import math

from Pythoncode.model.Vector import Vector
from Pythoncode.model.coordinate import Coordinate


def get_length(vector1: Coordinate, vector2: Coordinate) -> float:
    return math.sqrt(math.pow(vector1.x - vector2.x, 2) + math.pow(vector1.y - vector2.y, 2))


def get_vector(coordinate1: Coordinate, coordinate2: Coordinate) -> Vector:
    return Vector(coordinate2.x - coordinate1.x, coordinate2.y - coordinate1.y)


def get_vector_length(vector: Vector) -> float:
    length = math.sqrt(math.pow(vector.x, 2) + math.pow(vector.y, 2))
    return length


def calculate_angle_clockwise(coordinate1: Coordinate, coordinate2: Coordinate, center: Coordinate) -> float:
    vector1 = get_vector(coordinate1, center)
    vector2 = get_vector(coordinate2, center)
    dotproduct = (vector1.x * vector2.y - vector1.y * vector2.x)
    return -math.degrees(math.asin(
        dotproduct / (get_vector_length(vector1) * get_vector_length(vector2))))
