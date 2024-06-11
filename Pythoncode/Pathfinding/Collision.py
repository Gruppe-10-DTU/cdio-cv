import copy

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


def line_hits_rectangle(box: Rectangle, c1: Coordinate, c2: Coordinate):
    c1_copy = copy.deepcopy(c1)
    c2_copy = copy.deepcopy(c2)

    start = calculate_endpoint_outcode(box, c1_copy)
    end = calculate_endpoint_outcode(box, c2_copy)

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
                x = c1_copy.x + (c2_copy.x - c1_copy.x) * (box.c2.y - c1_copy.y) / (c2_copy.y - c1_copy.y)
                y = box.c2.y
            elif outside & BOTTOM:
                x = c1_copy.x + (c2_copy.x - c1_copy.x) * (box.c1.y - c1_copy.y) / (c2_copy.y - c1_copy.y)
                y = box.c1.y
            elif outside & LEFT:
                y = c1_copy.y + (c2_copy.y - c1_copy.y) * (box.c1.x - c1_copy.x) / (c2_copy.x - c1_copy.x)
                x = box.c1.x
            elif outside & RIGHT:
                y = c1_copy.y + (c2_copy.y - c1_copy.y) * (box.c2.x - c1_copy.x) / (c2_copy.x - c1_copy.x)
                x = box.c2.x

            if outside == start:
                c1_copy.x = x
                c1_copy.y = y
                start = calculate_endpoint_outcode(box, c1_copy)
            else:
                c2_copy.x = x
                c2_copy.y = y
                end = calculate_endpoint_outcode(box, c2_copy)

    return does_clip
