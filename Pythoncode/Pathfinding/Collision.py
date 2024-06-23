import copy

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Clipping import line_clips_rectangle
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.model.coordinate import Coordinate


def line_collides_with_rectangle(box: Rectangle, begin: Coordinate, to: Coordinate):
    if in_obstacle(box, to):
        return False

    return line_clips_rectangle(box, begin, to)


def robot_collides(box: Rectangle, begin: Coordinate, to: Coordinate, pixel_per_cm: int):
    left_p1, left_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                         VectorUtils.get_vector(begin, to),
                                                                         pixel_per_cm * 10, True)
    right_p1, right_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                           VectorUtils.get_vector(begin, to),
                                                                           pixel_per_cm * 10, False)
    collides = (line_collides_with_rectangle(box, begin, to) or
                line_collides_with_rectangle(box, left_p1, left_p2) or
                line_collides_with_rectangle(box, right_p1, right_p2))

    print("Center hit: " + str(line_collides_with_rectangle(box, begin, to)) + "\n" +
          "Left hit: " + str(line_collides_with_rectangle(box, left_p1, left_p2)) + "\n" +
          "Right hit: " + str(line_collides_with_rectangle(box, right_p1, right_p2)) + "\n")

    return collides


def in_obstacle(box: Rectangle, to: Coordinate):
    return box.c1.x <= to.x <= box.c2.x and box.c1.y <= to.y <= box.c2.y
