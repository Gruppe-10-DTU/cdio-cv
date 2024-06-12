import math
from Pythoncode.model import Ball
from Pythoncode.model.Vector import Vector
from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.Pathfinding.Collision import *
from Pythoncode.Pathfinding.VectorUtils import *
from Pythoncode.Pathfinding.CornerUtils import *
from Pythoncode.model.Corner import *
from Pythoncode.Pathfinding.CornerUtils import *


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate, obstacle: Rectangle):
        self.targets = targets
        self.start = start
        self.obstacle = obstacle

    def get_closest(self, point: Coordinate, drive_points: list) -> Coordinate:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = math.sqrt(math.pow(target.center.x - point.x, 2) + math.pow(target.center.y - point.y, 2))
            clips = line_hits_rectangle(self.obstacle, point, target.center)
            if not clips:
                if closest_distance > distance:
                    closest_distance = distance
                    m = target
        if m is None:
            for drive_point in drive_points:
                distance = math.sqrt(math.pow(drive_point.x - point.x,2) + math.pow(drive_point.y - point.y,2))
                if closest_distance > distance:
                    closest_distance = distance
                    m = drive_point
        return m

    def update_target(self, targets):
        self.targets = targets
