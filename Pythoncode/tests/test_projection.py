from unittest import TestCase

from Pythoncode.model.coordinate import Coordinate
from Pythoncode.Pathfinding.Projection import Projection


class TestProjection(TestCase):
    def test_projection_from_coordinate(self):
        projection = Projection(Coordinate(4, 4), 4)
        target = Coordinate(0, 0)

        projection.projection_from_coordinate(target, 1)
        self.assertEqual(1, target.x)
        self.assertEqual(1, target.y)

    def test_projection_from_tall_item(self):
        projection = Projection(Coordinate(4, 4), 100)
        target = Coordinate(0, 0)

        projection.projection_from_coordinate(target, 1)
        self.assertEqual(0.04, target.x)
        self.assertEqual(0.04, target.y)

    def test_projection_from_tall_item_weird_height(self):
        projection = Projection(Coordinate(4, 4), 100)
        target = Coordinate(0, 0)

        projection.projection_from_coordinate(target, 6)
        self.assertEqual(0.04*6, target.x)
        self.assertEqual(0.04*6, target.y)

    def test_projection_from_tall_item_inverse(self):
        projection = Projection(Coordinate(4, 4), 100)
        target = Coordinate(8, 8)

        projection.projection_from_coordinate(target, 1)
        self.assertEqual(7.96, target.x)
        self.assertEqual(7.96, target.y)

