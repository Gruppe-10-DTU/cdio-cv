from unittest import TestCase

from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.Pathfinding.Collision import line_hits_rectangle
from Pythoncode.model.coordinate import Coordinate


class Test(TestCase):
    def test_line_does_clip_corner_edge(self):
        box = Rectangle(Coordinate(10, 10), Coordinate(20, 20))
        x0 = 11
        y0 = 9
        x1 = 9
        y1 = 11

        clipped = line_hits_rectangle(box, Coordinate(x0, y0), Coordinate(x1, y1))

        self.assertTrue(clipped)

    def test_line_does_not_clip_corner_edge(self):
        box = Rectangle(Coordinate(10, 10), Coordinate(20, 20))

        x0 = 11
        y0 = 8
        x1 = 8
        y1 = 11

        clipped = line_hits_rectangle(box, Coordinate(x0, y0), Coordinate(x1, y1))

        self.assertFalse(clipped)

    def test_line_does_not_clip_outer(self):
        box = Rectangle(Coordinate(10, 10), Coordinate(20, 20))

        x0 = 1
        y0 = 1
        x1 = 4
        y1 = 4

        clipped = line_hits_rectangle(box, Coordinate(x0, y0), Coordinate(x1, y1))

        self.assertFalse(clipped)

    def test_line_does_not_clip_inside(self):
        box = Rectangle(Coordinate(10, 10), Coordinate(20, 20))

        x0 = 11
        y0 = 11
        x1 = 14
        y1 = 14

        clipped = line_hits_rectangle(box, Coordinate(x0, y0), Coordinate(x1, y1))

        self.assertFalse(clipped)
