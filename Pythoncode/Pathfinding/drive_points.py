from Pythoncode.model.coordinate import Coordinate
from Pythoncode.model.Corner import Placement
from Pythoncode.model.Vector import Vector
from Pythoncode.Pathfinding import CornerUtils

PRECICION = 15 # drive point tolereance
WALL_DISTANCE = 30 # wall clearance

class Drive_points:
    def __init__(self, corners, mapscale):
        self.corners = sorted(corners, key=lambda corner: corner.placement.value)
        self.scale = mapscale
        self.drive_points = []
        self.drive_points = self.__generate_drive_points()
        self.last = None

    def __generate_drive_points(self):
        left_wall = Vector(self.corners[0].center, self.corners[1].center)
        top_wall = Vector(self.corners[0].center, self.corners[2].center)
        right_wall = Vector(self.corners[2].center, self.corners[3].center)
        bottom_wall = Vector(self.corners[1].center, self.corners[3].center)
        for corner in self.corners:
            match corner.placement:
                case Placement.TOP_LEFT:
                    top_left = self.__calculate_corner_drive_point(corner, top_wall, left_wall)
                    #drive_points.append(top_left)
                    top_center = self.__calculate_center_drive_point(top_left, top_wall)
                    #drive_points.append(top_center)
                case Placement.TOP_RIGHT:
                    top_right = self.__calculate_corner_drive_point(corner, top_wall.invert(), right_wall)
                    #drive_points.append(top_right)
                    right_center = self.__calculate_center_drive_point(top_right, right_wall)
                    #drive_points.append(right_center)
                case Placement.BOTTOM_LEFT:
                    bottom_left = self.__calculate_corner_drive_point(corner, left_wall.invert(), bottom_wall)
                    #drive_points.append(bottom_left)
                    left_center = self.__calculate_center_drive_point(bottom_left, left_wall.invert())
                    #drive_points.append(left_center)
                case Placement.BOTTOM_RIGHT:
                    bottom_right = self.__calculate_corner_drive_point(corner, right_wall.invert(), bottom_wall.invert())
                    #drive_points.append(bottom_right)
                    bottom_center = self.__calculate_center_drive_point(bottom_right, bottom_wall.invert())
                    #drive_points.append(bottom_center)
        drive_points = [top_left, top_center, top_right, right_center, bottom_right, bottom_center, bottom_left,left_center]
        return drive_points

        
    def get_drive_points(self):
        return self.drive_points

    def get_next_drive_point(self, point: Coordinate) -> Coordinate:
        closest = None
        current = None
        distance = float('inf')
        for i in range(len(self.drive_points)):
            if self.drive_points[i] == self.last:
                continue
            tmp_distance = Vector(point,self.drive_points[i]).length()
            if tmp_distance < PRECICION * self.scale:
                self.last = self.drive_points[i]
                #current = self.drive_points[i]
                return self.drive_points[(i+1)%8]
            if tmp_distance > PRECICION * self.scale and tmp_distance < distance:
                distance = tmp_distance
                closest = self.drive_points[i]
        self.last = current
        return closest

    def get_closest_drive_point(self, point: Coordinate) -> Coordinate:
        closest = None
        distance = float('inf')
        for i in range(len(self.drive_points)):
            tmp_distance = Vector(point, self.drive_points[i]).length()
            if tmp_distance > PRECICION * self.scale and tmp_distance < distance:
                distance = tmp_distance
                closest = self.drive_points[i]
        return closest

    def get_closest_drive_point_vector(self, point) -> Vector:
        end = self.get_next_drive_point(point)
        return Vector(end.x - point.x, end.y - point.y)

    def is_on_drive_point(self, point: Coordinate) -> (bool, Coordinate):
        for i in range(len(self.drive_points)):
            tmp_distance = Vector(point,self.drive_points[i]).length()
            if tmp_distance < PRECICION * self.scale:
                return True, self.drive_points[i]
        return False, None


    def __calculate_corner_drive_point(self, corner, wall1, wall2) -> Coordinate:
        vec1 = wall1.scale(WALL_DISTANCE * self.scale / wall1.length())
        vec2 = wall2.scale( WALL_DISTANCE * self.scale / wall2.length())
        return corner.center.add_vector(vec1.add(vec2))

    def __calculate_center_drive_point(self, corner_point, wall ) -> Coordinate:
        vec = wall.scale_to_length((wall.length() - (WALL_DISTANCE * 2 * self.scale)) / 2)
        return corner_point.add_vector(vec)
