def is_edge_inside_box(edge, box):
    """Check if an edge is inside a box"""
    x_min, y_min, x_max, y_max = box
    x1, y1, x2, y2  = edge[:4]
    return (x_min <= x1 <= x_max and x_min <= x2 <= x_max and
            y_min <= y1 <= y_max and y_min <= y2 <= y_max)

def find_edge_in_boxes(edge, boxes):
    for box in boxes:
        if is_edge_inside_box(edge, box):
            return box
    return None

def calculate_averge_of_box(box):
    """Calculate the average of a box"""
    x_min, y_min, x_max, y_max = box
    return (x_min + x_max) / 2, (y_min + y_max) / 2

def can_draw_label(prev_room_index, room_index):
    if prev_room_index == -1:
        return True
    if prev_room_index != room_index:
        return True
    return False