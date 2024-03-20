from ultralytics import YOLO


model = YOLO("yolov8n.yaml")
model.train(data="dataset/data.yaml", epochs=11)