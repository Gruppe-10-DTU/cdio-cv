from unittest import TestCase

from Pythoncode.Pathfinding.drive_points import drive_points
from Pythoncode.model.Corner import Corner

class Test(TestCase):
    def test_drive_points(self):
        corners = []
        corners.append(Corner(0, 0, 10, 10, 0))
        corners.append(Corner(0, 100, 10, 100, 1))
        corners.append(Corner(100, 0, 110, 10, 2))
        corners.append(Corner(100, 100, 110, 110, 3))
        dp = drive_points(corners)
        self.assertEqual(len(dp.get_drive_points()), 8)
        start = dp.get_drive_points()[0]
        end = start
        for i in range(8):
            end = dp.get_closest_drive_point(end)

        self.assertEqual(start, end)

