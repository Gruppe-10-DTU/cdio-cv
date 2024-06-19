from Pythoncode.Pathfinding.Collision import line_hits_rectangle
from Pythoncode.model import Ball
from Pythoncode.Pathfinding.CornerUtils import *
from Pythoncode.model import Ball
from Pythoncode.model.Corner import *
from Pythoncode.model.Egg import Egg
from Pythoncode.model.Rectangle import Rectangle


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate, obstacle: Rectangle):
        self.targets = targets
        self.start = start
        self.obstacle = obstacle

    def get_closest(self, point: Coordinate) -> Ball:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = VectorUtils.get_length(target.center, point)
            clips = line_hits_rectangle(self.obstacle, point, target.center)

            if not clips and closest_distance > distance:
                closest_distance = distance
                m = target
        return m

    def update_target(self, targets):
        self.targets = targets
