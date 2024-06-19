import configparser
from unittest import TestCase

from Pythoncode.Pathfinding import CornerUtils
from Pythoncode.Pathfinding.CornerUtils import get_corners_as_list
from Pythoncode.model.Corner import Placement, Corner


class Test(TestCase):

    def test_all_corners_given(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')

        config.set('MAP', 'height', "120")
        config.set('MAP', 'width', "180")

        corners = {}

        corners[1] = Corner(0, 20, 20, 40, 1)
        corners[1].set_placement(Placement.TOP_LEFT)

        corners[2] = Corner(0, 200, 20, 220, 2)
        corners[2].set_placement(Placement.BOTTOM_LEFT)

        corners[3] = Corner(200, 20, 220, 40, 3)
        corners[3].set_placement(Placement.TOP_RIGHT)

        corners[4] = Corner(200, 200, 220, 220, 3)
        corners[4].set_placement(Placement.BOTTOM_RIGHT)

        list = get_corners_as_list(corners)
        count = CornerUtils.get_cm_per_pixel(corners=list, balls=[], config=config)
        #self.assertEqual(180/120, count)

    def test_next_corner(self):
        corners = {}

        corners[1] = Corner(0, 20, 20, 40, 1)
        corners[1].set_placement(Placement.TOP_LEFT)

        corners[2] = Corner(0, 200, 20, 220, 2)
        corners[2].set_placement(Placement.BOTTOM_LEFT)

        corners[3] = Corner(200, 20, 220, 40, 3)
        corners[3].set_placement(Placement.TOP_RIGHT)

        corners[4] = Corner(200, 200, 220, 220, 3)
        corners[4].set_placement(Placement.BOTTOM_RIGHT)


        corners = get_corners_as_list(corners)

        self.assertEqual(Placement.TOP_LEFT, corners[0].placement)
        self.assertEqual(Placement.TOP_RIGHT, CornerUtils.get_next(corners[0], corners).placement)

        self.assertEqual(Placement.BOTTOM_LEFT, corners[1].placement)
        self.assertEqual(Placement.TOP_LEFT, CornerUtils.get_next(corners[1], corners).placement)

        self.assertEqual(Placement.TOP_RIGHT, corners[2].placement)
        self.assertEqual(Placement.BOTTOM_RIGHT, CornerUtils.get_next(corners[2], corners).placement)

        self.assertEqual(Placement.BOTTOM_RIGHT, corners[3].placement)
        self.assertEqual(Placement.BOTTOM_LEFT, CornerUtils.get_next(corners[3], corners).placement)

