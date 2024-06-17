from Pythoncode.model.coordinate import Coordinate


class Rectangle:
    def __init__(self, c1: Coordinate, c2: Coordinate):
        self.c1 = c1
        self.c2 = c2

        self.center = Coordinate(c1.x + (c2.x - c1.x) / 2, c1.y + (c2.y - c1.y) / 2)
        self.c3 = Coordinate(c1.x, c2.y)
        self.c4 = Coordinate(c2.x, c1.y)
