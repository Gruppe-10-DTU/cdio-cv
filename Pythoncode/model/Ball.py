from Pythoncode.model.coordinate import Coordinate


class Ball:

    def __init__(self, x1, y1, x2, y2, id):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.id = id
        self.center = Coordinate(x1 + (x2-x1)/2, y1 + (y2-y1)/2)