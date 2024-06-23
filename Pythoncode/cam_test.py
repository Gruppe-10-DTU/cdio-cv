"""
Inspired by official ultralytics documentation on object tracking with YOLO.
Source: https://docs.ultralytics.com/modes/track/#persisting-tracks-loop
"""

import cv2

from ultralytics import YOLO

model = YOLO("./model/best.pt")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
width = 1280
height = 720

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

ret, frame = cap.read()

while ret:
    results = model.predict(frame, conf=0.5)
    annotated_frame = results[0].plot()
    cv2.imshow("YOLO", annotated_frame)
    if cv2.waitKey(1) == ord("q"):
        break

    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()
