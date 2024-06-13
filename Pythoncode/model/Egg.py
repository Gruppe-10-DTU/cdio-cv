from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.Pathfinding.VectorUtils import get_vector, get_vector_length


class Egg:
    def __init__(self, x1, y1, x2, y2, rectangle):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.center = Coordinate(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
        self.buffer_center = None
        self.buffer_c1 = None
        self.buffer_c2 = None

        buffer_dist = 4
        buffer_radius = 3

        direction = get_vector(rectangle.center,self.center)

        if direction.x == 0:
            if direction.y < 0:
                self.buffer_center = Coordinate(self.center.x, self.center.y - buffer_dist)
            else:
                self.buffer_center = Coordinate(self.center.x, self.center.y + buffer_dist)
        elif direction.x < 0 :
            if direction.y == 0:
                self.buffer_center = Coordinate(self.center.x - buffer_dist, self.center.y)
            elif direction.y < 0:
                self.buffer_center = Coordinate(self.center.x - buffer_dist, self.center.y - buffer_dist)
            else:
                self.buffer_center = Coordinate(self.center.x - buffer_dist, self.center.y + buffer_dist)
        else:
            if direction.y == 0:
                self.buffer_center = Coordinate(self.center.x + buffer_dist, self.center.y)
            elif direction.y < 0:
                self.buffer_center = Coordinate(self.center.x + buffer_dist, self.center.y - buffer_dist)
            else:
                self.buffer_center = Coordinate(self.center.x + buffer_dist, self.center.y + buffer_dist)


        self.buffer_c1 = Coordinate(self.buffer_center.x - buffer_radius, self.buffer_center.y + buffer_radius)
        self.buffer_c2 = Coordinate(self.buffer_center.x + buffer_radius, self.buffer_center.y - buffer_radius)
