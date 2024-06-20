from Pythoncode.Pathfinding.Collision import line_hits_rectangle, p_clips, in_obstacle
from Pythoncode.model import Ball
from Pythoncode.Pathfinding.CornerUtils import *
import drive_points
from Pythoncode.model import Ball
from Pythoncode.model.Corner import *
from Pythoncode.model.Rectangle import Rectangle


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate, obstacle: Rectangle, pixel_per_cm: float,
                 drive_points: drive_points.Drive_points):
        self.targets = targets
        self.start = start
        self.obstacle = obstacle
        self.pixel_per_cm = pixel_per_cm
        self.drive_points = drive_points


    def get_closest(self, point: Coordinate) -> Ball:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = VectorUtils.get_length(target.center, point)
            if in_obstacle(self.obstacle,target.center):
                best_vector = VectorUtils.get_vector(target.center,self.obstacle.center).scale(100)
                best_driving_point = self.drive_points.get_closest_drive_point(
                    point= Coordinate(self.obstacle.center.x + best_vector.x, self.obstacle.center.y + best_vector.y)
                )
                distance += VectorUtils.get_length(target.center,best_driving_point)
                clips = p_clips(self.obstacle, point, best_driving_point, int(self.pixel_per_cm))
            else:
                clips = p_clips(self.obstacle, point, target.center, pixel_per_cm= int(self.pixel_per_cm))

            if not clips and closest_distance > distance:
                closest_distance = distance
                m = target
        return m


    def update_target(self, targets):
        self.targets = targets
