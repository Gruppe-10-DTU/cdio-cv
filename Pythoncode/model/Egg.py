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


        distances = {"c1": (get_vector_length(get_vector(self.center, rectangle.c1))),
                     "c2": (get_vector_length(get_vector(self.center, rectangle.c2))),
                     "c3": (get_vector_length(get_vector(self.center, rectangle.c3))),
                     "c4": (get_vector_length(get_vector(self.center, rectangle.c4)))}

        sorted_distances = sorted(distances.items(), key=lambda x: x[1])
        distance_array = []
        i = 0
        for x in sorted_distances.keys():
            distance_array[i] = x
            var = i + 1

        self.buffer1 = None
        self.buffer2 = None
        if distance_array[0] == "c1"| "c3" & distance_array[1] == "c1"| "c3":
            self.buffer1 = c1
            self.buffer2 = distance_array[1]+7
        elif distance_array[0] == "c1"| "c4" & distance_array[1] == "c1"| "c4":
            self.buffer1 = distance_array[0]-7
            self.buffer2 = distance_array[1]+7


