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

def get_cm_per_pixel(corners):
    list = []
    for key, value in corners.items():
        list.append(value)

    sorted_list = sorted(list, key=lambda c: c.placement.value)
    match len(sorted_list):
        case 4:
            return VectorUtils.get_length(sorted_list[0].center, sorted_list[1].center) / 120
        case 3, 2:

            if sorted_list[0].placement % 2 == sorted_list[1].placement % 2:
                return VectorUtils.get_length(sorted_list[0].center, sorted_list[1].center) / 120
            elif sorted_list[0].placement % 2 == 1 and sorted_list[1].placement % 2 == 0:
                return VectorUtils.get_length(sorted_list[0].center, sorted_list[1].center) / 180
            else:
                """Udregner ud fra diagonalen"""
                return VectorUtils.get_length(sorted_list[0].center, sorted_list[1].center) / 216.33

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

