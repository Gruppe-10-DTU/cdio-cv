from unittest import TestCase

from model.Ball import Ball


class TestBall(TestCase):

    def test_center(self):
        ball = Ball(0, 20, 20, 20)
        self.assertEquals(ball.center, (10,10))
