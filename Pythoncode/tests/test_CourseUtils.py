from unittest import TestCase

from Pythoncode.model.Corner import Corner, Placement
from Pythoncode.Pathfinding.CornerUtils import set_placements
from Pythoncode.Pathfinding.CornerUtils import calculate_goals


class Test(TestCase):

    def test_less_than_four_corners_sets_none(self):
        corners = {0: Corner(0, 0, 0, 0, 0),
                   1: Corner(1, 1, 1, 1, 1),
                   2: Corner(2, 2, 2, 2, 2)}

        corners = set_placements(corners)

        self.assertIsNone(corners[0].placement)
        self.assertIsNone(corners[1].placement)
        self.assertIsNone(corners[2].placement)

    def test_more_than_four_corners_sets_none(self):
        corners = {0: Corner(0, 0, 0, 0, 0),
                   1: Corner(1, 1, 1, 1, 1),
                   2: Corner(2, 2, 2, 2, 2),
                   3: Corner(3, 3, 3, 3, 3),
                   4: Corner(4, 4, 4, 4, 4)}

        corners = set_placements(corners)

        self.assertIsNone(corners[0].placement)
        self.assertIsNone(corners[1].placement)
        self.assertIsNone(corners[2].placement)
        self.assertIsNone(corners[3].placement)
        self.assertIsNone(corners[4].placement)

    def test_top_left_to_bottom_right(self):
        corners = {0: Corner(0, 0, 1, 1, 0),
                   1: Corner(0, 10, 0, 11, 1),
                   2: Corner(10, 0, 11, 1, 2),
                   3: Corner(10, 10, 11, 11, 3)}

        corners = set_placements(corners)

        self.assertEqual(corners[0].placement, Placement.TOP_LEFT)
        self.assertEqual(corners[1].placement, Placement.BOTTOM_LEFT)
        self.assertEqual(corners[2].placement, Placement.TOP_RIGHT)
        self.assertEqual(corners[3].placement, Placement.BOTTOM_RIGHT)

    def test_bottom_right_to_top_left(self):
        corners = {0: Corner(100, 100, 110, 110, 0),
                   1: Corner(100, 0, 110, 10, 1),
                   2: Corner(0, 10, 0, 11, 2),
                   3: Corner(0, 0, 10, 10, 3)}

        corners = set_placements(corners)

        self.assertEqual(corners[0].placement, Placement.BOTTOM_RIGHT)
        self.assertEqual(corners[1].placement, Placement.TOP_RIGHT)
        self.assertEqual(corners[2].placement, Placement.BOTTOM_LEFT)
        self.assertEqual(corners[3].placement, Placement.TOP_LEFT)

    def test_calculate_goals(self):
        corners = {0: Corner(1, 1, 1, 1, 0),
                   1: Corner(1, 10, 1, 10, 1),
                   2: Corner(10, 0, 10, 0, 2),
                   3: Corner(10, 10, 10, 10, 3)}

        corners = set_placements(corners)
        goals = calculate_goals(corners)

        self.assertEqual(len(goals), 2)

        self.assertEqual(goals[0].x, 1.0)
        self.assertEqual(goals[0].y, 5.5)

        self.assertEqual(goals[1].x, 10.0)
        self.assertEqual(goals[1].y, 5.0)

