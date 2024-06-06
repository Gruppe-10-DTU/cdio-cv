import grpc
from ultralytics import YOLO
import cv2

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.grpc.gRPC_Class import gRPC_Class
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Robot import Robot
from Pythoncode.model.Vip import Vip
from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2

from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Corner import Corner
from Pythoncode.Pathfinding.CornerUtils import set_placements, calculate_goals

pixel_per_cm = 412/180


def main():
    model = YOLO("model/best.pt")
    # cap = cv2.VideoCapture('videos/with_egg.mp4')
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    ret, frame = cap.read()
    vip = None
    egg = None
    balls = []
    corners = {}
    goals = []

    if ret:
        results = model.track(frame, persist=True)

        displayFrame(results[0].plot())
        boxes = results[0].boxes.cpu()
        # track_ids = results[0].boxes.id.int().cpu().tolist()

        # Plot the tracks
        # for box, track_id in zip(boxes, track_ids):
        for box in boxes:
            if results[0].names[box.cls.item()] == "ball":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)
                balls.append(Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id))
            elif results[0].names[box.cls.item()] == "robot_front":
                x, y, w, h = box.xywh[0]
                robot_front = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "robot_body":
                x, y, w, h = box.xywh[0]
                robot_body = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "corner":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)
                corners[current_id] = Corner(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)
                print("Corner")
            elif results[0].names[box.cls.item()] == "obstacle":
                print("Cross")
            elif results[0].names[box.cls.item()] == "egg":
                print("Egg")
            elif results[0].names[box.cls.item()] == "orange_ball":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)

                vip = Vip(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)

        robot = Robot(robot_body, robot_front)
        corners = set_placements(corners)
        goals = calculate_goals(corners)
        pathfinding = Pathfinding(balls, robot_body)
        commandHandler(pathfinding, robot)
    ret, frame = cap.read()

    while ret:
        results = model.track(frame, persist=True)
        displayFrame(results[0].plot())

        # Press q to stop
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('p'):
            cv2.waitKey(-1)
        """
        for box in boxes:
            x, y, w, h = box.xywh[0]
            if results[0].names[box.cls.item()] == "ball":
                current_id = int(box.id)
                old_ball = balls[current_id]
                if old_ball.x1 != x or old_ball.y1 != y:
                    balls[box.id] = Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)
            """
        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()



def commandHandler(pathfinding, robot):
    with grpc.insecure_channel("172.20.10.12:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)

        while len(pathfinding.targets) > 0:
            target = pathfinding.get_closest()

            angle = VectorUtils.calculate_angle_clockwise(target.center, robot.front, robot.center)
            tmp = int(angle)

            #Robot can't take negative numbers, so can only turn right.
            if tmp < 0:
                tmp += 360

            stub.Turn(protobuf_pb2.TurnRequest(degrees=tmp))
            length = VectorUtils.get_length(target.center, robot.center)

            stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=int(length / pixel_per_cm), speed=700))

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            pathfinding.remove_target(target)


def displayFrame(frame_):
    frame2 = cv2.resize(frame_, (620, 480))
    cv2.imshow("YOLO", frame2)


if __name__ == '__main__':
    main()
