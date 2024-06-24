from Pythoncode.Pathfinding.Collision import robot_collides, in_obstacle
from Pythoncode.model import Ball, Egg
from Pythoncode.model.Corner import *
from Pythoncode.model.Rectangle import Rectangle


class Pathfinding:
    def __init__(self, targets: list[Ball], start: Coordinate, obstacle: Rectangle, pixel_per_cm: float,
                 drive_points):
        self.targets = targets
        self.start = start
        self.obstacle = obstacle
        self.pixel_per_cm = pixel_per_cm
        self.drive_points = drive_points

    def get_closest(self, point: Coordinate, egg: Egg) -> Ball:
        closest_distance = math.inf
        m = None
        for target in self.targets:
            distance = VectorUtils.get_length(target.center, point)
            if in_obstacle(self.obstacle, target.center):
                best_vector = VectorUtils.get_vector(self.obstacle.center, target.center)
                best_vector = best_vector.scale_to_length(350)
                vector_end_coordinate = Coordinate(self.obstacle.center.x + best_vector.x, self.obstacle.center.y + best_vector.y)
                best_driving_point = self.drive_points.get_closest_drive_point(point=vector_end_coordinate)
                distance += VectorUtils.get_length(target.center, best_driving_point)

                clips = robot_collides(self.obstacle, point, best_driving_point, int(self.pixel_per_cm))
                target.collection_point = best_driving_point
            elif egg.ball_inside_buffer(target.center):
                best_vector = VectorUtils.get_vector(egg.center, target.center)
                best_vector = best_vector.scale_to_length(350)
                vector_end_coordinate = Coordinate(egg.center.x + best_vector.x,
                                                   egg.center.y + best_vector.y)
                best_driving_point = self.drive_points.get_closest_drive_point(point=vector_end_coordinate)
                distance += VectorUtils.get_length(target.center, best_driving_point)

                clips = robot_collides(self.obstacle, point, best_driving_point, int(self.pixel_per_cm))
                target.collection_point = best_driving_point
            else:
                clips = robot_collides(self.obstacle, point, target.center, pixel_per_cm=int(self.pixel_per_cm))
            if not clips and closest_distance > distance:
                closest_distance = distance
                m = target
        return m


    def update_target(self, targets):
        self.targets = targets
