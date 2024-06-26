"""
Very loosely inspired by official ultralytics documentation on object tracking with YOLO.
Source:
Ultralytics, 2024: "Multi-Object Tracking with Ultralytics YOLO"
accessed 11.06.2024:
https://docs.ultralytics.com/modes/track/#persisting-tracks-loop
"""
import cv2
cap = cv2.VideoCapture("")
count = 0

ret, frame = cap.read()

while ret:
    cv2.imwrite(f"img/frame_{str(count).zfill(6)}.jpg", frame)
    count += 1

    if cv2.waitKey(1) == ord('q'):
        break

    ret, frame = cap.read()
