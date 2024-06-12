from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Corner import Corner
from Pythoncode.model.Vector import Vector
from Pythoncode.Pathfinding import CornerUtils

class drive_points:
    def __init__(self, corners):
        self.corners = CornerUtils.set_placements(corners)
        self.drive_points = []
        self.last = None
        self.scale = CornerUtils.get_cm_per_pixel(corners)
        self.generate_drive_points()

    def generate_drive_points(self):
        left_wall = Vector(self.corners[0].center, self.corners[1].center)
        top_wall = Vector(self.corners[0].center, self.corners[2].center)
        right_wall = Vector(self.corners[2].center, self.corners[3].center)
        bottom_wall = Vector(self.corners[1].center, self.corners[3].center)
        
        
        
    def get_drive_points(self):
        return self.drive_points

    def get_closest_drive_point(self, point) -> Coordinate:
        closest = None
        distance = None
        for drive_point in self.drive_points:
            if drive_point == self.last:
                continue
            tmp_distance = point.distance(drive_point)
            if tmp_distance > 5 * self.scale and tmp_distance < distance:
                distance = tmp_distance
                closest = drive_point
            elif tmp_distance < 5 * self.scale:
                self.last = drive_point
        return closest

    def get_closest_drive_point_vector(self, point) -> Vector:
        return Vector(point, self.get_closest_drive_point(point))
