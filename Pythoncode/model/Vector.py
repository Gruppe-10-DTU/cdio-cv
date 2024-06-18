import math
from Pythoncode.model.coordinate import Coordinate

class Vector:
    def __init__(self, x, y):
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            self.x = x
            self.y = y
        elif isinstance(x, Coordinate) and isinstance(y, Coordinate):
            self.x = y.x - x.x
            self.y = y.y - x.y
    
    def get_dot_product(self, other) -> float:
        return self.x * other.y - self.y * other.x

    def length(self) -> float:
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))

    def normalize(self):
        length = Vector.length(self)
        return self.__class__(self.x/length, self.y/length)
    def get_clockwise_angle(self, other) -> float:
        dotproduct = self.get_dot_product(other)
        other = other.get_dot_product(self)
        arctan2 = math.atan2(other, dotproduct)
        return math.degrees(arctan2)

    def add(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def scale(self, scalar):
        return self.__class__(self.x * scalar, self.y * scalar)

    def invert(self):
        return self.__class__(-self.x, -self.y)

    def scale_to_length(self, length):
        return self.scale(length / self.length())

    def orthogonal(self):
        return Vector(self.y, -self.x)
