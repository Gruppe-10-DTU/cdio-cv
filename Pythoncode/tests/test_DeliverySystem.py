import unittest
from unittest.mock import MagicMock

from Pythoncode.Pathfinding import VectorUtils, Collision
from Pythoncode.Pathfinding.DeliverySystem import deliver_balls_to_goal, align_robot_with_delivery_point, \
    calculate_delivery_point, calculate_alignment_point
from Pythoncode.model.CourtState import CourtState, CourtProperty
from Pythoncode.model.coordinate import Coordinate
from Pythoncode.grpc import protobuf_pb2 as protobuf__pb2, protobuf_pb2


class TestDeliverySystem(unittest.TestCase):

    def setUp(self):
        self.rpc = MagicMock()
        self.robot = MagicMock()
        self.drive_points = MagicMock()
        self.drive = MagicMock()

    def test_deliver_balls_to_goal(self):
        # Mocking the necessary properties
        CourtState.getProperty = MagicMock(side_effect=lambda x: {
            CourtProperty.OBSTACLE: [],
            CourtProperty.PIXEL_PER_CM: 1,
            CourtProperty.ROBOT: self.robot
        }[x])
        self.robot.center = Coordinate(0, 0)
        self.robot.front = Coordinate(1, 0)
        self.drive_points.get_drive_points = MagicMock(return_value=[Coordinate(0, 0) for _ in range(8)])
        self.drive_points.get_next_drive_point = MagicMock(return_value=Coordinate(1, 1))
        Collision.robot_collides = MagicMock(return_value=False)

        deliver_balls_to_goal(self.rpc, self.robot, self.drive_points, self.drive, big_goal=True)

        self.rpc.Vacuum.assert_called_once_with(protobuf__pb2.VacuumPower(power=False))

    def test_align_robot_with_delivery_point(self):
        robot = MagicMock()
        drive_point = Coordinate(0, 0)
        delivery_point = Coordinate(5, 5)

        CourtState.getProperty = MagicMock(side_effect=lambda x: {
            CourtProperty.PIXEL_PER_CM: 1,
            CourtProperty.ROBOT: robot
        }[x])
        robot.center = Coordinate(0, 0)
        robot.front = Coordinate(1, 0)
        VectorUtils.get_length = MagicMock(side_effect=[10, 10, 2, 1])
        VectorUtils.calculate_angle_clockwise = MagicMock(return_value=45)

        result = align_robot_with_delivery_point(robot, drive_point, delivery_point, self.rpc)
        self.assertTrue(result)

    def test_calculate_delivery_point(self):
        robot = MagicMock()
        alignment_point = Coordinate(0, 0)
        drive_points = MagicMock()
        drive_points.get_drive_points = MagicMock(return_value=[Coordinate(1, 1) for _ in range(8)])
        CourtState.getProperty = MagicMock(return_value=1)

        result = calculate_delivery_point(robot, alignment_point, drive_points, big_goal=True)
        self.assertIsInstance(result, Coordinate)

    def test_calculate_alignment_point(self):
        drive_point = Coordinate(0, 0)
        delivery_point = Coordinate(5, 5)
        CourtState.getProperty = MagicMock(return_value=1)

        result = calculate_alignment_point(drive_point, delivery_point)
        self.assertIsInstance(result, Coordinate)

if __name__ == '__main__':
    unittest.main()