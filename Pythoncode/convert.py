from ultralytics import YOLO

model = YOLO("model/best.pt")
model.export(format="pt", half=True)
