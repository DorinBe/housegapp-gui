def is_edge_inside_box(edge, box):
    """Check if an edge is inside a box"""
    box_x1, box_y1, box_x2, box_y2 = box
    x_min = min(box_x1, box_x2)
    x_max = max(box_x1, box_x2)
    y_min = min(box_y1, box_y2)
    y_max = max(box_y1, box_y2)

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

def reorganize_json(data):
    original_room_types = data["room_type"]
    original_boxes = data["boxes"]
    original_edges = data["edges"]
    original_ed_rm = data["ed_rm"]

    new_json = {
        "room_types": [],
        "rooms": {
        }
    }
    from_edge_index = 0
    to_edge_index = 0
    prev_room_index = 0
    curr_room_index = 0
    for to_edge_index, ed_rm in enumerate(original_ed_rm):

        curr_room_index = ed_rm[0]
        if (prev_room_index != curr_room_index):
            room_or_door= "room" if original_room_types[prev_room_index] <10 else "door"
            new_room = {prev_room_index:{"edges": original_edges[from_edge_index:to_edge_index],
                                         "ed_rm": original_ed_rm[from_edge_index:to_edge_index],
                                         "boxes": original_boxes[prev_room_index],
                                         "room_type": original_room_types[prev_room_index]}}
            
            new_json["rooms"].update(new_room)
            from_edge_index = to_edge_index
            prev_room_index = curr_room_index
    return new_json

        
if (__name__ == "__main__"):
    import json
    with open("ParseJsons\\1736.json") as f:
        data = json.load(f)
        data = reorganize_json(data)
        for room in data["rooms"].items():
            for edge in room[1]["edges"]:
                print(edge)
            print(room)
        print("debug newjson")