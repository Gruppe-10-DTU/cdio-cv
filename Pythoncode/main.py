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

pixel_per_cm = 10


def main():
    model = YOLO("model/best.pt")
    # cap = cv2.VideoCapture('videos/with_egg.mp4')
    cap = cv2.VideoCapture(0)
    print("Cam works")
    ret, frame = cap.read()
    vip = None
    egg = None
    balls = {}
    corners = []

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
                balls[current_id] = Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)
            elif results[0].names[box.cls.item()] == "robot_front":
                x, y, w, h = box.xywh[0]
                robot_front = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "robot_body":
                x, y, w, h = box.xywh[0]
                robot_body = Coordinate(int(x), int(y))
            elif results[0].names[box.cls.item()] == "corner":
                # Left cornor of video is 0,0 which can be used to find the position of each corner.
                # Iffy if less than 4 corners are found
                x, y, w, h = box.xywh[0]

                print(int(x), int(y), int(x) + int(w), int(y) + int(h))
            elif results[0].names[box.cls.item()] == "obstacle":
                print("Cross")
            elif results[0].names[box.cls.item()] == "egg":
                print("Egg")
            elif results[0].names[box.cls.item()] == "orange_ball":
                x, y, w, h = box.xywh[0]
                current_id = int(box.id)

                vip = Vip(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)

        # robot = Robot(robot_body, robot_front)
        # pathfinding = Pathfinding(balls, robot_front)
        # commandHandler(pathfinding, robot)

    ret, frame = cap.read()

    while ret:
        results = model.track(frame, persist=True)
        displayFrame(results[0].plot())
        # pathfinding.display_items()

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


"""
def commandHandler(pathfinding, robot):
    with grpc.insecure_channel("172.20.10.12:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)

        while len(pathfinding.targets) > 0:
            target = pathfinding.get_closest()

            angle = VectorUtils.calculate_angle_clockwise(target.center, robot.front, robot.center)
            stub.Turn(angle)
            length = VectorUtils.get_length(target.center, robot.center)

            stub.Move(True, length / pixel_per_cm, 30)

"""


def displayFrame(frame_):
    frame2 = cv2.resize(frame_, (620, 480))
    cv2.imshow("YOLO", frame2)


if __name__ == '__main__':
    main()
