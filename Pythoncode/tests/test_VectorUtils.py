from unittest import TestCase

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.Vector import Vector
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

    def test_calculate_parallel_vector_coordinates(self):
        start = Coordinate(1, 1)
        vector = Vector(1, 1)
        distance = 2.8284271247461903  # sqrt(2^2 + 2^2)

        c1, c2 = VectorUtils.calculate_parallel_vector_coordinates(start, vector, distance, True)
        c3, c4 = VectorUtils.calculate_parallel_vector_coordinates(start, vector, distance, False)

        self.assertEqual(- 1, c1.x)
        self.assertEqual(3, c1.y)
        self.assertEqual(0, c2.x)
        self.assertEqual(4, c2.y)

        self.assertEqual(3, c3.x)
        self.assertEqual(- 1, c3.y)
        self.assertEqual(4, c4.x)
        self.assertEqual(0, c4.y)
