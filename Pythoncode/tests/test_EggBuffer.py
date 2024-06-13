from unittest import TestCase

from Pythoncode.model.Egg import Egg
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.model.coordinate import Coordinate


class TestEggBuffer(TestCase):

    def test_buffer_coordinates(self):
        obstacle = Rectangle(Coordinate(-10, 10), Coordinate(10, -10))
        egg = Egg(0, 2, 2, 0, obstacle)
        self.assertEqual(obstacle.center.x, 0)
        self.assertEqual(obstacle.center.y, 0)
        self.assertEqual(egg.center.x, 1)
        self.assertEqual(egg.center.y, 1)

        self.assertEqual(egg.buffer_center.x, 5)
        self.assertEqual(egg.buffer_center.y, 5)

        self.assertEqual(egg.buffer_c1.x, 2)
        self.assertEqual(egg.buffer_c1.y, 8)
        self.assertEqual(egg.buffer_c2.x, 8)
        self.assertEqual(egg.buffer_c2.y, 2)

    def test_buffer_coordinates_down(self):
        obstacle = Rectangle(Coordinate(1, 1), Coordinate(3, 3))
        egg = Egg(6, -2, 8, -4, obstacle)


        self.assertEqual(egg.buffer_c1.x, 8)
        self.assertEqual(egg.buffer_c1.y, -4)
        self.assertEqual(egg.buffer_c2.x, 14)
        self.assertEqual(egg.buffer_c2.y, -10)

    def test_buffer_coordinates_on_same_axes(self):
        obstacle = Rectangle(Coordinate(-1, 1), Coordinate(1, -1))
        egg = Egg(-1, 4, 1, 2, obstacle)


        self.assertEqual(egg.buffer_c1.x, -3)
        self.assertEqual(egg.buffer_c1.y, 10)
        self.assertEqual(egg.buffer_c2.x, 3)
        self.assertEqual(egg.buffer_c2.y, 4)