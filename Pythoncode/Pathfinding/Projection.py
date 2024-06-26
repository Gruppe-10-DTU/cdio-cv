from Pythoncode.model.coordinate import Coordinate
import numpy as np

from Pythoncode.model.coordinate import Coordinate

class Projection:
    def __init__(self, camera: Coordinate, height: float):
        self.camera = camera
        self.height = height

    def projection_from_coordinate(self, target: Coordinate, height: float) -> Coordinate:
        v = np.array([self.camera.x - target.x, self.camera.y - target.y, self.height])
        normalize = v * (height / v[2])
        target.x += normalize[0]
        target.y += normalize[1]

        return target
