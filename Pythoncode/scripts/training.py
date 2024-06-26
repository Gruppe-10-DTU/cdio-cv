"""
Source for the specific YOLO model variant usage:
Github, 2023: "Small object under 15px detection"
accessed 20.03.2024
https://github.com/ultralytics/ultralytics/issues/981
"""

from ultralytics import YOLO
import torch

# Model specific for training small objects
model = YOLO("yolov8s-p2.yaml").load("yolov8s.pt")

if __name__ == "__main__":

    device = "cpu"
    # use CUDA cores when available
    if torch.cuda.is_available():
        device = 0

    model.train(data="data/data.yaml", epochs=100, imgsz=1120, device=device, batch=-1)
