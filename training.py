from ultralytics import YOLO

model = YOLO("yolov8s-p2.yaml").load("yolov8s.pt")

if __name__ == "__main__":
    # Note that device=0 only works with CUDA cores
    model.train(data="data/data.yaml", epochs=6, imgsz=1000, device=0, batch=-1)
