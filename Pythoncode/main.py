import cv2
from ultralytics import YOLO

from Pythoncode.Pathfinding.Pathfinding import Pathfinding
from Pythoncode.model.Ball import Ball
from Pythoncode.model.Corner import Corner
from Pythoncode.model.Robot import Robot
from Pythoncode.model.Vip import Vip
from Pythoncode.model.coordinate import Coordinate
from Pythoncode.Pathfinding.CornerUtils import set_placements

def main():
    model = YOLO("../model/best.pt")
    cap = cv2.VideoCapture('../video/with_egg.mp4')

    ret, frame = cap.read()
    vip = None
    egg = None
    balls = {}
    corners = {}

    if ret:
        results = model.track(frame, persist=True)

        display_frame(results[0].plot())
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
        dijk = Pathfinding(balls, robot_front)
        closest = dijk.get_closest()
        corners = set_placements(corners)
        print(corners)

    ret, frame = cap.read()

    while ret:
        results = model.track(frame, persist=True)
        display_frame(results[0].plot())
        dijk.display_items()

        # Press q to stop
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('p'):
            cv2.waitKey(-1)

        for box in boxes:
            x, y, w, h = box.xywh[0]
            if results[0].names[box.cls.item()] == "ball":
                current_id = int(box.id)
                old_ball = balls[current_id]
                if old_ball.x1 != x or old_ball.y1 != y:
                    balls[box.id] = Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)

        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()


def display_frame(frame_):
    frame2 = cv2.resize(frame_, (620, 480))
    cv2.imshow("YOLO", frame2)


if __name__ == '__main__':
    main()
