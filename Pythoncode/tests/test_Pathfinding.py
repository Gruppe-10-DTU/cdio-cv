from unittest import TestCase

from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.model.Ball import Ball
from Pythoncode.model.coordinate import Coordinate


class TestPathfinding(TestCase):

    def test_pathfind(self):
        list_balls = [Ball(0, 20, 20, 40, 1), Ball(20, 40, 40, 60, 2), Ball(50, 70, 70, 90, 3)]
        start = Coordinate(100,100)

        pathfinding = Pathfinding(list_balls, start)

        ball = pathfinding.get_closest(start)
        self.assertEqual(ball.id, 3)

        pathfinding.remove_target(ball)

        ball = pathfinding.get_closest(ball.center)
        self.assertEqual(ball.id, 2)

        pathfinding.remove_target(ball)


        ball = pathfinding.get_closest(ball.center)
        self.assertEqual(ball.id, 1)

        pathfinding.remove_target(ball)


