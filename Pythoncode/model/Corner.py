from Pythoncode.model.coordinate import Coordinate
from enum import Enum


class Corner:
    def __init__(self, x1, y1, x2, y2, tracking_id):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.center = Coordinate(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
        self.id = tracking_id
        self.placement = None

    def set_placement(self, placement):
        if isinstance(placement, Placement):
            self.placement = placement


class Placement(Enum):
    TOP_LEFT = 1
    BOTTOM_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_RIGHT = 4
