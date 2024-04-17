from ultralytics import YOLO
import cv2

from Pathfinding.Pathfinding import Pathfinding
from model.Ball import Ball
from model.coordinate import Coordinate

model = YOLO("model/best.pt")
cap = cv2.VideoCapture('videos/with_egg.mp4')

ret, frame = cap.read()

balls = {}

if ret:
    results = model.track(frame, persist=True)

    frame_ = results[0].plot()
    cv2.imshow("YOLO", frame_)
    boxes = results[0].boxes.cpu()
    # track_ids = results[0].boxes.id.int().cpu().tolist()


    # Plot the tracks
    # for box, track_id in zip(boxes, track_ids):
    for box in boxes:
        if results[0].names[box.cls.item()] == "ball":
            x, y, w, h = box.xywh[0]
            current_id = int(box.id)
            balls[current_id] = Ball(int(x), int(y), int(x) + int(w), int(y) + int(h), current_id)
    dijk = Pathfinding(balls, Coordinate(0, 0))
ret, frame = cap.read()

while ret:
    results = model.track(frame, persist=True)
    frame_ = results[0].plot()
    cv2.imshow("YOLO", frame_)

    # Press q to stop
    if cv2.waitKey(1) == ord('q'):
        break

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
