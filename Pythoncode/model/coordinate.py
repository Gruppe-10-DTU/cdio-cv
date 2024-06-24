class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add_vector(self, vector):
        return Coordinate(self.x + vector.x, self.y + vector.y)



    def to_tuble(self) -> tuple:
        return self.x, self.y
