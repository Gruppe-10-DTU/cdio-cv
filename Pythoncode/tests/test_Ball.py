from unittest import TestCase

from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner


class TestBall(TestCase):

    def test_center(self):
        ball = Ball(0, 20, 20, 40, 1)
        self.assertEquals(ball.center.x, 10.0)
        self.assertEquals(ball.center.y, 30.0)
    
    def test_distance_to_wall(self):
        ball = Ball(65, 35, 55, 45, 1)
        corner1 = Corner(5, 5, 15, 15)
        corner2 = Corner(95, 5, 105, 15)
        distance = ball.get_distance_to_wall(corner1, corner2)
        self.assertEquals(distance, 30.0)
        
