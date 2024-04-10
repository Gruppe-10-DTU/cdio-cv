from ultralytics import YOLO
import cv2

model = YOLO("model/best.pt")
cap = cv2.VideoCapture(0)

ret, frame = cap.read()
while ret:

    results = model.track(frame, persist=True)
    frame_ = results[0].plot()
    cv2.imshow("YOLO", frame_)

    # Press q to stop
    if cv2.waitKey(1) == ord('q'):
        break

    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()
