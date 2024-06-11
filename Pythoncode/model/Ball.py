from Pythoncode.model.coordinate import Coordinate
from Pythoncode.Pathfinding import VectorUtils


class Ball:

    def __init__(self, x1, y1, x2, y2, id):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.id = id
        self.center = Coordinate(x1 + (x2-x1)/2, y1 + (y2-y1)/2)

    def get_distance_to_wall(self, corner1, corner2):
        wall = VectorUtils.get_vector(corner1.x1, corner1.y1, corner2.x1, corner2.y1)
        corner_corner = VectorUtils.get_length(wall)
        c1_ball = VectorUtils.get_vector(corner1.x1, corner1.y1, self.center.x, self.center.y)

        return abs(c1_ball.get_dot_product(wall))/abs(corner_corner)
