import copy

from Pythoncode.Pathfinding import VectorUtils, drive_points
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.model.coordinate import Coordinate

"""
This is an implementation of the Cohen-Sutherland algorithm for line clipping
If a line is clipped to fit the rectangle, a collision is detected.
"""

LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def calculate_endpoint_outcode(box: Rectangle, coordinate: Coordinate):
    outcode = 0

    if coordinate.x < box.c1.x:
        outcode |= LEFT
    elif coordinate.x > box.c2.x:
        outcode |= RIGHT

    if coordinate.y < box.c1.y:
        outcode |= BOTTOM
    elif coordinate.y > box.c2.y:
        outcode |= TOP

    return outcode


def line_hits_rectangle(box: Rectangle, begin: Coordinate, to: Coordinate):
    if in_obstacle(box, to):
        return False

    c1 = copy.deepcopy(begin)
    c2 = copy.deepcopy(to)

    start = calculate_endpoint_outcode(box, c1)
    end = calculate_endpoint_outcode(box, c2)

    does_clip = False
    run = True

    while run:
        if not (start | end):
            does_clip = True
            run = False
        elif start & end:
            run = False
        else:
            outside = start if start > end else end
            x = 0
            y = 0

            if outside & TOP:
                x = c1.x + (c2.x - c1.x) * (box.c2.y - c1.y) / (c2.y - c1.y)
                y = box.c2.y
            elif outside & BOTTOM:
                x = c1.x + (c2.x - c1.x) * (box.c1.y - c1.y) / (c2.y - c1.y)
                y = box.c1.y
            elif outside & LEFT:
                y = c1.y + (c2.y - c1.y) * (box.c1.x - c1.x) / (c2.x - c1.x)
                x = box.c1.x
            elif outside & RIGHT:
                y = c1.y + (c2.y - c1.y) * (box.c2.x - c1.x) / (c2.x - c1.x)
                x = box.c2.x

            if outside == start:
                c1.x = x
                c1.y = y
                start = calculate_endpoint_outcode(box, c1)
            else:
                c2.x = x
                c2.y = y
                end = calculate_endpoint_outcode(box, c2)

    return does_clip

def p_clips(box: Rectangle, begin: Coordinate, to: Coordinate, pixel_per_cm: int):
    left_p1, left_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                         VectorUtils.get_vector(begin, to),
                                                                         pixel_per_cm * 10, True)
    right_p1, right_p2 = VectorUtils.calculate_parallel_vector_coordinates(begin,
                                                                           VectorUtils.get_vector(begin, to),
                                                                           pixel_per_cm * 10, False)
    clips = (line_hits_rectangle(box, begin, to) or
             line_hits_rectangle(box, left_p1, left_p2) or
             line_hits_rectangle(box, right_p1, right_p2))
    print("Center hit: " + str(line_hits_rectangle(box, begin, to)) + "\n" +
          "Left hit: " + str(line_hits_rectangle(box, left_p1, left_p2)) + "\n" +
          "Right hit: " + str(line_hits_rectangle(box, right_p1, right_p2)) + "\n")

    return clips


def in_obstacle(box: Rectangle, to: Coordinate):
    return box.c1.x <= to.x <= box.c2.x and box.c1.y <= to.y <= box.c2.y


