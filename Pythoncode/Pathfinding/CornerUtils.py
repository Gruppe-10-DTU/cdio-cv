import math

from Pythoncode.Pathfinding import VectorUtils
from Pythoncode.model.Corner import Placement
from Pythoncode.model.Goal import Goal


def set_placements(corners):
    if len(corners) == 4:
        sorted_list = sorted(corners.items(), key=lambda c: c[1].x1)
        left_most = sorted_list[:2]
        right_most = sorted_list[2:]
        top_left_most = sorted(left_most, key=lambda c: c[1].y1)
        top_right_most = sorted(right_most, key=lambda c: c[1].y1)

        corners[top_left_most[0][1].id].set_placement(Placement.TOP_LEFT)
        corners[top_left_most[1][1].id].set_placement(Placement.BOTTOM_LEFT)
        corners[top_right_most[0][1].id].set_placement(Placement.TOP_RIGHT)
        corners[top_right_most[1][1].id].set_placement(Placement.BOTTOM_RIGHT)
    return corners

def get_corners_as_list(corners):
    list = []
    for key, value in corners.items():
        list.append(value)
    return sorted(list, key=lambda c: c.placement.value)

def get_next(corner, corners):
    if corner.placement == 1:
        return corners[2]
    elif corner.placement == 2:
        return corners[0]
    elif corner.placement == 3:
        return corners[3]
    elif corner.placement == 4:
        return corners[1]
    return None



def get_cm_per_pixel(corners, config):
    height = float(config.get('MAP', 'height'))
    width = float(config.get('MAP', 'width'))
    match len(corners):
        case 4:
            return VectorUtils.get_length(corners[0].center, corners[1].center) / height
        case 3, 2:

            if corners[0].placement % 2 == corners[1].placement % 2:
                return VectorUtils.get_length(corners[0].center, corners[1].center) / width
            elif corners[0].placement % 2 == 1 and corners[1].placement % 2 == 0:
                return VectorUtils.get_length(corners[0].center, corners[1].center) / width
            else:
                """Udregner ud fra diagonalen"""
                return VectorUtils.get_length(corners[0].center, corners[1].center) / math.sqrt(math.pow(height, 2) + math.pow(width, 2))

    """Default value"""
    return 2.0

def calculate_goals(corners) -> list:
    goals = []
    sorted_list = sorted(corners.items(), key=lambda c: c[1].placement.value)
    if len(sorted_list) >= 2:
        if sorted_list[0][1].placement == Placement.TOP_LEFT and sorted_list[1][1].placement == Placement.BOTTOM_LEFT:
            x1 = sorted_list[0][1].center.x
            x2 = sorted_list[1][1].center.x
            y1 = sorted_list[0][1].center.y
            y2 = sorted_list[1][1].center.y
            goals.append(Goal(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2))

        sorted_list.reverse()
        if sorted_list[0][1].placement == Placement.BOTTOM_RIGHT and sorted_list[1][1].placement == Placement.TOP_RIGHT:
            x1 = sorted_list[1][1].center.x
            x2 = sorted_list[0][1].center.x
            y1 = sorted_list[1][1].center.y
            y2 = sorted_list[0][1].center.y
            goals.append(Goal(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2))

    return goals
