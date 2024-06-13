import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_dot_product(self, other) -> float:
        return self.x * other.y - self.y * other.x

    def length(self) -> float:
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))

    def get_clockwise_angle(self, other) -> float:
        dotproduct = self.get_dot_product(other)
        other = other.get_dot_product(self)
        arctan2 = math.atan2(other, dotproduct)
        return math.degrees(arctan2)

    def add(self, other) -> Vector:
        return Vector(self.x + other.x, self.y + other.y)

    def scale(self, scalar) -> Vector:
        return Vector(self.x * scalar, self.y * scalar)

    def invert(self) -> Vector:
        return Vector(-self.x, -self.y)

    def scale_to_length(self, length) -> Vector:
        return self.scale(length / self.length())
