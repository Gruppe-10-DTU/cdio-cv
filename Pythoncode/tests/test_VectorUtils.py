from unittest import TestCase

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.coordinate import Coordinate


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

    def test_calculate_angle_135(self):
        center = Coordinate(0, 0)
        coordinate2 = Coordinate(1, 1)
        coordinate1 = Coordinate(-2, 0)

        angle = VectorUtils.calculate_angle_clockwise(coordinate1, coordinate2, center)

        self.assertEqual(135, angle)

    def test_calculate_angle_negative_135(self):
        center = Coordinate(0, 0)
        coordinate1 = Coordinate(1, 1)
        coordinate2 = Coordinate(-2, 0)

        angle = VectorUtils.calculate_angle_clockwise(coordinate1, coordinate2, center)

        self.assertEqual(-135, angle)

    def test_calculate_angle_180(self):
        center = Coordinate(0, 0)
        coordinate2 = Coordinate(1, 0)
        coordinate1 = Coordinate(-2, 0)

        angle = VectorUtils.calculate_angle_clockwise(coordinate1, coordinate2, center)

        self.assertEqual(180, abs(angle))

    def test_calculate_angle_45(self):
        center = Coordinate(0, 0)
        front = Coordinate(1, 1)
        target = Coordinate(1, 0)

        angle = VectorUtils.calculate_angle_clockwise(target, front, center)

        self.assertEqual(-45, angle)

    def test_calculate_angle_negative_45(self):
        center = Coordinate(0, 0)
        front = Coordinate(1, 1)
        target = Coordinate(0, 1)

        angle = VectorUtils.calculate_angle_clockwise(target, front, center)

        self.assertEqual(45, angle)
