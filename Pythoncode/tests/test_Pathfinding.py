from unittest import TestCase

from Pythoncode.Pathfinding.Collision import line_hits_rectangle
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Rectangle import Rectangle
from Pythoncode.model.coordinate import Coordinate


class TestPathfinding(TestCase):
    """Just an outline for now. Have to wait for PAC to finish his code with drive_points so that I can test optimally."""
    def test_pathfind_with_obstacle_clipping(self):
        list_balls = [Ball(21,23 , 23, 29, 1), Ball(2,100,2,100,2),Ball(50, 10, 10, 70, 3)]
        start = Coordinate(1, 1)
        drive_points = [Coordinate(45,45), Coordinate(100,100)]
        pathfinding = Pathfinding(targets=list_balls, start=start, obstacle=Rectangle(Coordinate(20, 20), Coordinate(30,30)))

        ball = pathfinding.get_closest(start,drive_points)
        self.assertEqual(list_balls[1].center.x,ball.center.x)
        list_balls.pop()
        self.assertEqual(len(list_balls),2)
        ball = pathfinding.get_closest(start,drive_points)
        self.assertEqual(list_balls[1].center.x, ball.center.x)
        list_balls.pop()
        ball = pathfinding.get_closest(start,drive_points)
        self.assertEqual(drive_points.pop(),ball)


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


