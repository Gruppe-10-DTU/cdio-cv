import threading

import cv2

from ultralytics import YOLO

from Pythoncode.model.CourtState import CourtState

model = YOLO("./model/best.pt")

cv2.namedWindow("YOLO", cv2.WINDOW_FULLSCREEN)
thread = threading.Thread(target = CourtState.frameThread)
thread.start()
while True:
    frame = CourtState.getFrame()
    if frame is not None:
        results = model.track(frame, persist=True)
        annotated_frame = results[0].plot()

        cv2.imshow("YOLO", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()

print("Joining thread")
thread.join(1)
print("Stopped")
