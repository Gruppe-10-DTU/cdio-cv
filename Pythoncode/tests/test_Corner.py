import unittest
from unittest import TestCase

from Pythoncode.model.Corner import Corner, Placement
from Pythoncode.model.coordinate import Coordinate


class Test(TestCase):

    def test_ball_in_corner(self):
        corners = {}

        corners[1] = Corner(0, 20, 20, 40, 1)
        corners[1].set_placement(Placement.TOP_LEFT)

        corners[2] = Corner(0, 800, 20, 820, 2)
        corners[2].set_placement(Placement.BOTTOM_LEFT)

        corners[3] = Corner(800, 20, 820, 40, 3)
        corners[3].set_placement(Placement.TOP_RIGHT)

        corners[4] = Corner(800, 800, 820, 820, 4)
        corners[4].set_placement(Placement.BOTTOM_RIGHT)

        balls = [Coordinate(18, 25), Coordinate(4, 4), Coordinate(0, 0), Coordinate(201, 205)]
        self.assertTrue(corners[1].is_in_corner(balls[0]))

        self.assertFalse(corners[2].is_in_corner(balls[1]))

        self.assertFalse(corners[3].is_in_corner(balls[2]))

        self.assertFalse(corners[4].is_in_corner(balls[3]))


if __name__ == '__main__':
    unittest.main()
