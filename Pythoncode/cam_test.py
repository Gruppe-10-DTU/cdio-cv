import cv2

from ultralytics import YOLO

model = YOLO("./model/best.pt")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
width = 1920
height = 1080

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        results = model.track(frame, persist=True)
        annotated_frame = results[0].plot()
        cv2.imshow("YOLO", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break