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

        if rectangle.coordinate_inside_rectangle(self.center):
            #TODO: Gør boksen til et rektangle ud fra center af bolden i retning væk fra center.
            test = Vector(rectangle.center, self.center).scale_to_length(15)

            self.buffer_center = self.center.add_vector(test)
            buffer_radius = round(get_vector_length(get_vector(rectangle.center, self.buffer_center)) / 2, 2)
        else:
            self.buffer_center = self.center
            buffer_radius = round(
                get_vector_length(get_vector(Coordinate(self.x1, self.y1), self.buffer_center)) * buffer_dist, 2)

        self.buffer_radius = buffer_radius

        self.buffer_c1 = Coordinate(round(self.buffer_center.x - buffer_radius, 2),
                                    round(self.buffer_center.y - buffer_radius, 2))
        self.buffer_c2 = Coordinate(round(self.buffer_center.x + buffer_radius, 2),
                                    round(self.buffer_center.y + buffer_radius, 2))
        self.buffer = Rectangle(self.buffer_c1, self.buffer_c2)




    def ball_inside_buffer(self, target: Coordinate):
        top_left = self.buffer.c1.x <= target.x <= self.buffer.c2.x
        bottom_right = self.buffer.c1.y <= target.y <= self.buffer.c2.y
        return top_left and bottom_right
