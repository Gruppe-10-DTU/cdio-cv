"""
This code uses an implementation of the Cohen-Sutherland algorithm for line clipping

Source:
dilli_hangraei, 2024: "Line Clipping Algorithm ~ Part I"
accessed 18.06.2024:
https://medium.com/@dillihangrae/line-clipping-algorithm-part-i-6db9e8ce4cce
"""
import copy

from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Rectangle import Rectangle

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


def line_clips_rectangle(box: Rectangle, begin: Coordinate, to: Coordinate) -> bool:
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
