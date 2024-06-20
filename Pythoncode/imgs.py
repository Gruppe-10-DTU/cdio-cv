# Saves an image for every frame in a given video capture (use with CVAT annotations)

import cv2
cap = cv2.VideoCapture("")
count = 0
max_count = 0

ret, frame = cap.read()

while ret and max_count >= count:
    cv2.imwrite(f"img/frame_{str(count).zfill(6)}.jpg", frame)
    count += 1

    if cv2.waitKey(1) == ord('q'):
        break

    ret, frame = cap.read()
