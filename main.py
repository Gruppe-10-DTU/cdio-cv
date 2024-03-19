from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import cv2

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture("vid/Overview_Video.mp4")

ret = True
while ret:
    ret, frame = cap.read()

    results = model.predict(frame)

    for result in results:
        annotator = Annotator(frame)
        boxes = result.boxes
        for box in boxes:
            cords = box.xyxy[0]
            cls = box.cls
            conf = box.conf

            label = f"{model.names[int(cls)]} {float(conf):0.2f}"
            annotator.box_label(cords, label)

    img = annotator.result()
    cv2.imshow("YOLO", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
