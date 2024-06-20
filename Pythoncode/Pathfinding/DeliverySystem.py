from Pythoncode.main import pixel_per_cm
from Pythoncode.model.coordinate import Coordinate
from Pythoncode.Pathfinding import VectorUtils, Collision
from Pythoncode.model.CourtState import CourtState, CourtProperty
from Pythoncode.model import Vector
from Pythoncode.grpc import protobuf_pb2




def deliver_balls_to_goal(rpc, robot, drive_points, drive, big_goal=True):
    obstacle = CourtState.getProperty(CourtProperty.OBSTACLE)
    target_drive_point_index = 3 if big_goal else 7
    target_drive_point = drive_points.get_drive_points()[target_drive_point_index]
    # Drive to the target drive point
    while Collision.line_hits_rectangle(obstacle, robot.center, target_drive_point):
        route_point = drive_points.get_closest_drive_point(robot.center)
        # Move using the supplied drive function (it the one from main)
        drive(rpc, robot, route_point)

        # Not sure if this is needed
        CourtState.updateObjects(drive_points.drive_points, route_point)
    

    delivery_point = calculate_delivery_point(robot, target_drive_point, drive_points, big_goal)
    alignment_point = calculate_alignment_point(target_drive_point, delivery_point)
    alignment_successful = align_robot_with_delivery_point(robot, alignment_point, delivery_point, rpc)
    if alignment_successful:
        # 3: Turn off the motor to release balls (done)
        rpc.Vacuum(protobuf_pb2.VacuumPower(power=False))
        print("Balls delivered successfully!")
    else:
        # Failed to align. need to implement realignment
        print("Alignment failed. Cannot deliver balls.")


def align_robot_with_delivery_point(robot, drive_point: Coordinate, delivery_point: Coordinate, rpc) -> bool:
    while VectorUtils.get_length(robot.center, drive_point) > 1 * pixel_per_cm:
        angle = VectorUtils.calculate_angle_clockwise(drive_point, robot.front, robot.center)
        move_direction = True
        # turn opposite and reverese if it is shorter
        if angle > 90:
            angle = angle - 180
            move_direction = False
        elif angle < -90:
            angle = angle + 180
            move_direction = False
        # Slowly turn the robot and move it to the drive point
        rpc.Turn(protobuf_pb2.TurnRequest(angle=angle, speed=25))
        offset = VectorUtils.get_length(robot.center, delivery_point)
        rpc.Move(protobuf_pb2.MoveRequest(direction=move_direction, distance=int(offset),speed=25))
    # point the robot to the delivery point
    angle = VectorUtils.calculate_angle_clockwise(delivery_point, robot.front, robot.center)
    if angle > 3:
        rpc.Turn(protobuf_pb2.TurnRequest(angle=angle, speed=25))
    # Move the robot to the delivery point
    delivery_distance = VectorUtils.get_length(robot.front, delivery_point) - 3 * pixel_per_cm
    rpc.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(delivery_distance), speed=25))
    offset = VectorUtils.get_length(robot.front, delivery_point)
    return offset < 4.0



def calculate_delivery_point(robot, alignment_point, drive_points, big_goal):
    helper_index = 2 if big_goal else 6
    # Requires checking that the orthogonal is returned in the right direction
    # otherwise just invert it
    helper_vector = Vector(alignment_point, drive_points.get_drivepoints()[helper_index]).orthogonal().scale_to_length(25 * pixel_per_cm)
    goal_point = alignment_point.add_vector(helper_vector)
    drive_vector = Vector(robot.center, goal_point)
    delivery_point = robot.center.add(drive_vector)
    return delivery_point

# Simply moved the point the robot lines up at a bit closer to the wall
# to reduce driving distance
def calculate_alignment_point(drive_point, delivery_point):
    alignment_vector = Vector(drive_point, delivery_point).scale_to_length(5 * pixel_per_cm)
    return drive_point.add_vector(alignment_vector)
