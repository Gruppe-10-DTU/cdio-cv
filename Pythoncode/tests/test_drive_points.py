from unittest import TestCase

from Pythoncode.Pathfinding.drive_points import drive_points
from Pythoncode.model.Corner import Corner, Placement

class Test(TestCase):
    def test_drive_points(self):
        top_left = Corner(0, 0, 10, 10, 0)
        top_left.set_placement(Placement.TOP_LEFT)
        
        top_right = Corner(0, 100, 10, 110, 1)
        top_right.set_placement(Placement.TOP_RIGHT)

        bottom_left = Corner(100, 0, 110, 110, 2)
        bottom_left.set_placement(Placement.BOTTOM_LEFT)

        bottom_right = Corner(100, 100, 110, 110, 3)
        bottom_right.set_placement(Placement.BOTTOM_RIGHT)

        corners = [top_left, top_right, bottom_left, bottom_right]
        dp = drive_points(corners, 1.0)
        self.assertEqual(len(dp.get_drive_points()), 8)
        
        start = dp.get_drive_points()[0]
        end = start
        for i in range(8):
            end = dp.get_closest_drive_point(end)

        self.assertEqual(start, end)

