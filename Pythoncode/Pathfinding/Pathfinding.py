import math

from Pythoncode.model import Ball
from Pythoncode.model.coordinate import Coordinate


class Pathfinding:
    def __init__(self, targets, start: Coordinate):
        self.targets = targets
        self.start = start
        self.map = {}
        for target in targets.items():
            self.map[target[0]] = math.inf
        self.find_closest()

    def find_closest(self):
        start = self.start
        for target in self.targets.items():
            distance = math.sqrt(math.pow(target[1].center.x - start.x, 2) + math.pow(target[1].center.y - start.y, 2))
            self.map[target[0]] = distance
        self.map = sorted(self.map.items(), key=lambda x: x[1])

    def get_closest(self):
        return self.map[0]

    def remove_target(self, ball: Ball):
        del self.map[ball]
        self.find_closest()

    def update_target(self, targets):
        self.targets = targets
        self.find_closest()

    def display_items(self):
        print(self.map)
