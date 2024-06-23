from unittest import TestCase

from Pythoncode.Pathfinding.drive_points import Drive_points
from Pythoncode.model.Corner import Corner, Placement

class Test(TestCase):
    def test_drive_points_generation(self):
        top_left = Corner(0, 0, 10, 10, 1)
        top_left.set_placement(Placement.TOP_LEFT)
        
        top_right = Corner(100, 0, 110, 10, 2)
        top_right.set_placement(Placement.TOP_RIGHT)

        bottom_left = Corner(0, 100, 10, 110, 3)
        bottom_left.set_placement(Placement.BOTTOM_LEFT)

        bottom_right = Corner(100, 100, 110, 110, 4)
        bottom_right.set_placement(Placement.BOTTOM_RIGHT)

        corners = [top_left, bottom_left, top_right, bottom_right]
        dp = Drive_points(corners, 1.0)
        self.assertEqual(len(dp.get_drive_points()), 8)


    def test_all_drive_points_on_course(self):
        top_left = Corner(0, 0, 10, 10, 1)
        top_left.set_placement(Placement.TOP_LEFT)

        top_right = Corner(100, 0, 110, 10, 2)
        top_right.set_placement(Placement.TOP_RIGHT)
        bottom_left = Corner(0, 100, 10, 110, 3)
        bottom_left.set_placement(Placement.BOTTOM_LEFT)
        bottom_right = Corner(100, 100, 110, 110, 4)
        bottom_right.set_placement(Placement.BOTTOM_RIGHT)
        corners = [top_left, bottom_left, top_right, bottom_right]
        dp = Drive_points(corners, 1.0)
        self.assertEqual(len(dp.get_drive_points()), 8)
        points = dp.get_drive_points()
        for point in points:
            self.assertLess(top_left.center.x, point.x)
            self.assertLess(top_left.center.y, point.y)
            self.assertGreater(bottom_right.center.x, point.x)
            self.assertGreater(bottom_right.center.y, point.y)

    def test_drive_points_return_circular_order(self):
        top_left = Corner(0, 0, 10, 10, 1)
        top_left.set_placement(Placement.TOP_LEFT)

        top_right = Corner(100, 0, 110, 10, 2)
        top_right.set_placement(Placement.TOP_RIGHT)
        bottom_left = Corner(0, 100, 10, 110, 3)
        bottom_left.set_placement(Placement.BOTTOM_LEFT)
        bottom_right = Corner(100, 100, 110, 110, 4)
        bottom_right.set_placement(Placement.BOTTOM_RIGHT)
        corners = [top_left, bottom_left, top_right, bottom_right]
        dp = Drive_points(corners, 1.0)
         
        start = dp.get_drive_points()[0]
        current = start
        previous = None
        for i in range(8):
            next = dp.get_next_drive_point(current)
            self.assertNotEqual(previous, next)
            previous = current
            current = next


        self.assertEqual(start, current)
