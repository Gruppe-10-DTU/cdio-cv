from unittest import TestCase

from Pathfinding import VectorUtils
from model.coordinate import Coordinate


class Test(TestCase):
    def test_calculate_angle_clockwise(self):
        center = Coordinate(0, 0)
        coordinate1 = Coordinate(0, 1)
        coordinate2 = Coordinate(1, 0)

        angle = VectorUtils.calculate_angle_clockwise(coordinate1, coordinate2, center)

        self.assertEqual(90, angle)

    def test_calculate_angle_clockwise_counterclockwise(self):
        center = Coordinate(0, 0)
        coordinate2 = Coordinate(0, 1)
        coordinate1 = Coordinate(1, 0)

        angle = VectorUtils.calculate_angle_clockwise(coordinate1, coordinate2, center)

        self.assertEqual(-90, angle)
