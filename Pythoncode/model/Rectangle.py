import math

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.coordinate import Coordinate


def get_closest_points(point: Coordinate, candidates: [Coordinate]) -> [Coordinate, Coordinate]:
    distance = math.inf
    closest = None
    second_closest = None
    for p in candidates:
        tmp = VectorUtils.get_length(p, point)
        if tmp < distance:
            closest = p
            distance = tmp
    distance = math.inf

    index = candidates.index(closest)

    for p in candidates:
        if p == candidates[index]:
            continue
        tmp = VectorUtils.get_length(p, point)

        if tmp < distance:
            second_closest = p
            distance = tmp

    return closest, second_closest


class Rectangle:
    def __init__(self, c1: Coordinate, c2: Coordinate):

        self.c1 = c1
        self.c2 = c2

        self.c3 = Coordinate(c1.x, c2.y)
        self.c4 = Coordinate(c2.x, c1.y)
        self.center = Coordinate(c1.x + (c2.x - c1.x) / 2, c1.y + (c2.y - c1.y) / 2)

    def coordinate_inside_rectangle(self, target: Coordinate):
        top_left = self.c1.x <= target.x <= self.c2.x
        bottom_right = self.c1.y <= target.y <= self.c2.y
        return top_left and bottom_right