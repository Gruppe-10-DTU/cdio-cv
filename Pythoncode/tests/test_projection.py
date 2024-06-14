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
