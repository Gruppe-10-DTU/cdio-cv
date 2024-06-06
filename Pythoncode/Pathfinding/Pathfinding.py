import math

from Pythoncode.model import Ball
from Pythoncode.model.coordinate import Coordinate


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate):
        self.targets = targets
        self.start = start

    def get_closest(self, point: Coordinate) -> Ball:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = math.sqrt(math.pow(target.center.x - point.x, 2) + math.pow(target.center.y - point.y, 2))
            if closest_distance > distance:
                closest_distance = distance
                m = target
        return m

    def remove_target(self, ball: Ball):
        self.targets.remove(ball)

    def update_target(self, targets):
        self.targets = targets

