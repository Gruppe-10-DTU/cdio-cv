from unittest import TestCase

from model.Ball import Ball
from model.coordinate import Coordinate


class TestBall(TestCase):

    def test_center(self):
        ball = Ball(0, 20, 20, 40, 1)
        self.assertEquals(ball.center.x, 10.0)
        self.assertEquals(ball.center.y, 30.0)

