from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Corner import Corner, Placement
from Pythoncode.model.Vector import Vector
from Pythoncode.Pathfinding import CornerUtils

PRECICION = 5
WALL_DISTANCE = 25

class drive_points:
    def __init__(self, corners):
        self.corners = CornerUtils.set_placements(corners)
        self.drive_points = []
        self.last = None
        self.scale = CornerUtils.get_cm_per_pixel(corners)
        self.generate_drive_points()

    def __generate_drive_points(self):
        left_wall = Vector(self.corners[0].center, self.corners[1].center)
        top_wall = Vector(self.corners[0].center, self.corners[2].center)
        right_wall = Vector(self.corners[2].center, self.corners[3].center)
        bottom_wall = Vector(self.corners[1].center, self.corners[3].center)
        
        for corner in self.corners:
            match corner.placement:
                case Placement.TOP_LEFT:
                    top_left = self.calculate_corner_drive_point(corner, top_wall, left_wall)
                    self.drive_points.append(top_left)
                    top_center = self.calculate_center_drive_point(top_left, top_wall)
                    self.drive_points.append(top_center)
                    break
                case Placement.TOP_RIGHT:
                    top_right = self.calculate_corner_drive_point(corner, top_wall.invert(), right_wall)
                    self.drive_points.append(top_right)
                    right_center = self.calculate_center_drive_point(top_right, right_wall)
                    self.drive_points.append(right_center)
                    break
                case Placement.BOTTOM_LEFT:
                    bottom_left = self.calculate_corner_drive_point(corner, left_wall.invert(), bottom_wall)
                    self.drive_points.append(bottom_left)
                    left_center = self.calculate_center_drive_point(bottom_left, left_wall.invert())
                    self.drive_points.append(left_center)
                    break
                case Placement.BOTTOM_RIGHT:
                    bottom_right = self.calculate_corner_drive_point(corner, right_wall.invert(), bottom_wall.invert())
                    self.drive_points.append(bottom_right)
                    bottom_center = self.calculate_center_drive_point(bottom_right, bottom_wall.invert())
                    self.drive_points.append(bottom_center)
                    break

        
    def get_drive_points(self):
        return self.drive_points

    def get_closest_drive_point(self, point) -> Coordinate:
        closest = None
        distance = None
        for drive_point in self.drive_points:
            if drive_point == self.last:
                continue
            tmp_distance = point.distance(drive_point)
            if tmp_distance < PRECICION * self.scale:
                self.last = drive_point
            if tmp_distance > PRECICION * self.scale and tmp_distance < distance:
                distance = tmp_distance
                closest = drive_point
        return closest

    def get_closest_drive_point_vector(self, point) -> Vector:
        end = self.get_closest_drive_point(point)
        return Vector(end.x - point.x, end.y - point.y)

    def __calculate_corner_drive_point(self,corner, wall1, wall2) -> Coordinate:
        vec1 = wall1.scale(WALL_DISTANCE * self.scale / wall1.length())
        vec2 = wall2.scale( WALL_DISTANCE * self.scale / wall2.length())
        return corner.center.add_vector(vec1.add(vec2))

    def __calculate_center_drive_point(self, corner_point, wall ) -> Coordinate:
        vec = wall.scale_to_length((wall.length() / 2) - (WALL_DISTANCE * 2 * self.scale))
        return corner_point.add_vector(vec)
