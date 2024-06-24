from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Vector import Vector


class Ball:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.center = Coordinate(x1 + (x2-x1)/2, y1 + (y2-y1)/2)
        self.collection_point = None

    def get_distance_to_wall(self, corner1, corner2):
        wall = Vector(corner2.center.x - corner1.center.x, corner2.center.y - corner1.center.y)
        corner_corner = wall.length()
        c1_ball = Vector(self.center.x - corner1.center.x, self.center.y - corner1.center.y)
        return abs(c1_ball.get_dot_product(wall))/abs(corner_corner)


