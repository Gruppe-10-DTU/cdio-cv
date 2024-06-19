from Pythoncode.model.Ball import Ball
from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.Pathfinding.VectorUtils import get_vector, get_vector_length


class Egg:


    def __init__(self, x1, y1, x2, y2, rectangle = None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.buffer_radius = 0.0
        self.center = Coordinate(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
        if rectangle is not None:
            self.calculate_buffers(rectangle)

    def calculate_buffers(self, rectangle):

        buffer_dist = 1.5

        self.buffer_center = Coordinate(buffer_dist * self.center.x + (1 - buffer_dist) * rectangle.center.x,
                                        buffer_dist * self.center.y + (1 - buffer_dist) * rectangle.center.y)

        buffer_radius = round(get_vector_length(get_vector(rectangle.center, self.buffer_center)) / 2, 2)
        self.buffer_radius = buffer_radius
        self.buffer_c1 = Coordinate(round(self.buffer_center.x - buffer_radius, 2),
                                    round(self.buffer_center.y - buffer_radius, 2))
        self.buffer_c2 = Coordinate(round(self.buffer_center.x + buffer_radius, 2),
                                    round(self.buffer_center.y + buffer_radius, 2))
        self.buffer = Rectangle(self.buffer_c1, self.buffer_c2)

    def ball_inside_buffer(self, target: Ball):
        top_left = self.buffer.c1.x <= target.center.x <= self.buffer.c2.x
        bottom_right = self.buffer.c1.y <= target.center.y <= self.buffer.c2.y
        return top_left and bottom_right
