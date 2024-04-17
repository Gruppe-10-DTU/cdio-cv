from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.coordinate import Coordinate


class Robot:
    def __init__(self, center: Coordinate, front: Coordinate):
        self.front = front
        self.center = center

    def get_centerline(self):
        return VectorUtils.get_vector(self.front.x, self.front.y)
