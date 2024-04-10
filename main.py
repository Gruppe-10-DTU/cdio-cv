from ultralytics import YOLO
import cv2
from queue import PriorityQueue

from model.Ball import Ball

model = YOLO("model/best.pt")
cap = cv2.VideoCapture('overview.mp4')

ret, frame = cap.read()

balls = {}

if ret:
    results = model.track(frame, persist=True)
    boxes = results[0].boxes.cpu()
    #track_ids = results[0].boxes.id.int().cpu().tolist()

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Plot the tracks
    #for box, track_id in zip(boxes, track_ids):
    for box in boxes:
        if results[0].names[box.cls.item()] == "ball":
            x, y, w, h = box.xywh[0]

            balls[box.id] = Ball(x, y, x + w, y + h, box.id)

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
            old_ball = balls[box.id]
            if old_ball.x1 != x or old_ball.y1 != y:
                balls[box.id] = Ball(x, y, x + w, y + h)

    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()
