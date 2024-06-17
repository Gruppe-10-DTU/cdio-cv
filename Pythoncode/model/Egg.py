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

        buffer_dist = 2

        self.buffer_center = Coordinate(buffer_dist * self.center.x + (1-buffer_dist)*rectangle.center.x, buffer_dist * self.center.y + (1-buffer_dist)*rectangle.center.y)

        buffer_radius = round(get_vector_length(get_vector(rectangle.center, self.buffer_center)) / 2, 2)

        self.buffer_c1 = Coordinate(round(self.buffer_center.x - buffer_radius, 2), round(self.buffer_center.y + buffer_radius, 2))
        self.buffer_c2 = Coordinate(round(self.buffer_center.x + buffer_radius, 2), round(self.buffer_center.y - buffer_radius, 2))
