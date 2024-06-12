from unittest import TestCase

from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner


class TestBall(TestCase):

    def test_center(self):
        ball = Ball(0, 20, 20, 40, 1)
        self.assertEqual(ball.center.x, 10.0)
        self.assertEqual(ball.center.y, 30.0)
    
    def test_distance_to_wall(self):
        ball = Ball(4.5, 3.5, 5.5, 4.5, 1)
        corner1 = Corner(0.5, 0.5, 1.5, 1.5, 2)
        corner2 = Corner(7.5, 0.5, 8.5, 1.5, 3)
        distance = ball.get_distance_to_wall(corner1, corner2)
        self.assertEqual(distance, 3.0)
        
