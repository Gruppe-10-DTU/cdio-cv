from Pythoncode.Pathfinding.Collision import line_hits_rectangle
from Pythoncode.model import Ball
from Pythoncode.Pathfinding.CornerUtils import *
from Pythoncode.model import Ball
from Pythoncode.model.Corner import *
from Pythoncode.model.Rectangle import Rectangle


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate, obstacle: Rectangle, pixel_per_cm: float):
        self.targets = targets
        self.start = start
        self.obstacle = obstacle
        self.pixel_per_cm = pixel_per_cm

    def get_closest(self, point: Coordinate) -> Ball:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = VectorUtils.get_length(target.center, point)
            left_p1, left_p2 = VectorUtils.calculate_parallel_vector_coordinates(point, target.center, self.pixel_per_cm * 10, True)
            right_p1, right_p2 = VectorUtils.calculate_parallel_vector_coordinates(point, target.center, self.pixel_per_cm * 10, False)
            clips = line_hits_rectangle(self.obstacle, point, target.center) or line_hits_rectangle(self.obstacle, left_p1, left_p2) or line_hits_rectangle(self.obstacle, right_p1, right_p2)
            if not clips and closest_distance > distance:
                closest_distance = distance
                m = target
        return m

    def update_target(self, targets):
        self.targets = targets
