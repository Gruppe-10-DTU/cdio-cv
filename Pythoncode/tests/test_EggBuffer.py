from unittest import TestCase

from Pythoncode.model.Egg import Egg
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.model.coordinate import Coordinate


class TestEggBuffer(TestCase):

    def test_buffer_coordinates(self):
        obstacle = Rectangle(Coordinate(-10, 10), Coordinate(10, -10))
        egg = Egg(0, 2, 2, 0, obstacle)

        self.assertEqual(egg.buffer_center.x, 1.0)
        self.assertEqual(egg.buffer_center.y, 1.0)
        self.assertEqual(egg.buffer_c1.x, -1.12)
        self.assertEqual(egg.buffer_c1.y, -1.12)
        self.assertEqual(egg.buffer_c2.x, 3.12)
        self.assertEqual(egg.buffer_c2.y, 3.12)

    def test_buffer_coordinates_down(self):
        obstacle = Rectangle(Coordinate(1, 1), Coordinate(3, 3))
        egg = Egg(6, -2, 8, -4, obstacle)


        self.assertEqual(egg.buffer_c1.x, 4.88)
        self.assertEqual(egg.buffer_c1.y, -5.12)
        self.assertEqual(egg.buffer_c2.x, 9.12)
        self.assertEqual(egg.buffer_c2.y, -0.88)

    def test_buffer_coordinates_on_same_axes(self):
        obstacle = Rectangle(Coordinate(-1, 1), Coordinate(1, -1))
        egg = Egg(-1, 4, 1, 2, obstacle)


        self.assertEqual(egg.buffer_c1.x, -2.12)
        self.assertEqual(egg.buffer_c1.y, 0.88)
        self.assertEqual(egg.buffer_c2.x, 2.12)
        self.assertEqual(egg.buffer_c2.y, 5.12)