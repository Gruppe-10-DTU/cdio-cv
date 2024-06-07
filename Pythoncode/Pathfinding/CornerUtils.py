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
    sorted_list = sorted(corners.items(), key=lambda c: c[1].placement.value)
    if sorted_list[0][1].placement == Placement.TOP_LEFT and sorted_list[1][1].placement == Placement.BOTTOM_LEFT:
        return VectorUtils.get_length(sorted_list[0][1].center, sorted_list[1][1].center) / 180
    return 0


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


