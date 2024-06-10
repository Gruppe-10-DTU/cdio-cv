from unittest import TestCase

from Pythoncode.Pathfinding import CornerUtils
from Pythoncode.model.Corner import Placement, Corner


class Test(TestCase):

    def test_all_corners_given(self):
        corners = {}

        corners[1] = Corner(0, 20, 20, 40, 1)
        corners[1].set_placement(Placement.TOP_LEFT)

        corners[2] = Corner(0, 200, 20, 220, 2)
        corners[2].set_placement(Placement.BOTTOM_LEFT)

        corners[3] = Corner(200, 20, 220, 40, 3)
        corners[3].set_placement(Placement.TOP_RIGHT)

        corners[4] = Corner(200, 200, 220, 220, 3)
        corners[4].set_placement(Placement.BOTTOM_RIGHT)

        corners = CornerUtils.set_placements(corners)
        count = CornerUtils.get_cm_per_pixel(corners)
        self.assertEqual(180/120, count)

