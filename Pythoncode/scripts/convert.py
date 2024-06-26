"""
Source:
Ultralytics, 2024: Model Export with Ultralytics YOLO
accessed 02.04.2024:
https://docs.ultralytics.com/modes/export/#usage-examples
"""
from ultralytics import YOLO

model = YOLO("../model/best.pt")
model.export(format="pt", half=True)
