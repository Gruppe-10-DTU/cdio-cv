import cv2

from ultralytics import YOLO

model = YOLO("./model/best.pt")

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

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

cap.release()
cv2.destroyAllWindows()