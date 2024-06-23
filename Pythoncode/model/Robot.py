from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.Vector import Vector
from Pythoncode.model.coordinate import Coordinate


class Robot:
    def __init__(self, center: Coordinate, front: Coordinate):
        self.front = front
        self.center = center

    def get_centerline_as_vector(self):
        return Vector(self.front, self.center)
