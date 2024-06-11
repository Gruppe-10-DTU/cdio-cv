import math
from Pythoncode.model import Ball
from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.Pathfinding.Collision import *


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate, obstacle: Rectangle):
        self.targets = targets
        self.start = start
        self.obstacle = obstacle

    def get_closest(self, point: Coordinate) -> Ball:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = math.sqrt(math.pow(target.center.x - point.x, 2) + math.pow(target.center.y - point.y, 2))
            if not line_hits_rectangle(self.obstacle, point, Coordinate(target.center.x, target.center.y)):
                if closest_distance > distance:
                    closest_distance = distance
                    m = target
                    """""We could probably remove else-if statement later. This is just a temporary solution, 
                    so that I don't have to refactor before being able to communicate with original author."""
            elif self.obstacle is None:
                if closest_distance > distance:
                    closest_distance = distance
                    m = target
        """"To make sure that in case everything is behind an obstacle, we simply chose the last option for now."""""
        if m is None:
            m = target
        return m

    def remove_target(self, ball: Ball):
        self.targets.remove(ball)

    def update_target(self, targets):
        self.targets = targets
