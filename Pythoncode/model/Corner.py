import math

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.coordinate import Coordinate
from enum import Enum


class Corner:

    def __init__(self, x1, y1, x2, y2,id):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.center = Coordinate(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
        self.placement = None
        self.id = id

    def set_placement(self, placement):
        if isinstance(placement, Placement):
            self.placement = placement

    def is_in_corner(self, target: Coordinate) -> bool:
        leng = math.floor(VectorUtils.get_vector(target, self.center).length())
        return leng <= 150


class Placement(Enum):
    TOP_LEFT = 1
    BOTTOM_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_RIGHT = 4

