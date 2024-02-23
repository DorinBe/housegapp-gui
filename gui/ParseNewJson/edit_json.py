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

def fix_difference_between_edge_to_box(edge, box):
    replacedX = replacedY = False
    ex1, ey1, ex2, ey2 = edge[:4]
    bx1, by1, bx2, by2 = box
    room_index = edge[4]
    room_neighbour_index = edge[5]

    # replace edges
    if ex1>ex2:
        temp = ex1
        ex1 = ex2
        ex2 = temp
        replacedX = True

    if ey1>ey2:
        temp = ey1
        ey1 = ey2
        ey2 = temp
        replacedY = True

    if ex1<bx1:
        print(f"ex1 {ex1} < bx1 {bx1}, direfrencing to ex1=bx1 {bx1}")
        ex1 = bx1
    if ex2>bx2:
        print(f"ex2 {ex2} > bx2 {bx2}, direfrencing to ex2=bx2 {bx2}")
        ex2 = bx2
    if ey1<by1:
        print(f"ey1 {ey1} < by1 {by1}, direfrencing to ey1=by1 {by1}")
        ey1 = by1
    if ey2>by2:
        print(f"ey2 {ey2} > by2 {by2}, direfrencing to ey2=by2 {by2}")
        ey2 = by2

    if replacedX:
        temp = ex1
        ex1 = ex2
        ex2 = temp
    if replacedY:
        temp = ey1
        ey1 = ey2
        ey2 = temp

    return ex1, ey1, ex2, ey2,room_index, room_neighbour_index

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
    new_json["room_types"].extend(original_room_types)
    for to_edge_index, ed_rm in enumerate(original_ed_rm):

        curr_room_index = ed_rm[0]
        if (prev_room_index != curr_room_index):
            new_room = {prev_room_index:{"edges": original_edges[from_edge_index:to_edge_index],
                                         "ed_rm": original_ed_rm[from_edge_index:to_edge_index],
                                         "boxes": original_boxes[prev_room_index],
                                         "room_type": original_room_types[prev_room_index]}}
            
            new_json["rooms"].update(new_room)
            from_edge_index = to_edge_index
            prev_room_index = curr_room_index
    return new_json


def collect_ed_rm(json_data):
    ed_rm_list = []  # Initialize an empty list to hold the ed_rm values
    for room_id, room_data in json_data.items():  # Iterate through each room in the JSON
        ed_rm_list.extend(room_data.get('ed_rm', []))  # Use .get() to avoid KeyError and extend to flatten the list
    return ed_rm_list

def from_new_format_to_original_format(reorganized_json):
    original_json = {
        "room_type": [],
        "boxes": [],
        "edges": [],
        "ed_rm": []
    }

    original_json["room_type"].extend(reorganized_json["room_types"])
    original_json["ed_rm"].extend(collect_ed_rm(reorganized_json["rooms"]))

    for room in reorganized_json["rooms"].items():
        edges = room[1]["edges"]
        boxes = room[1]["boxes"]

        original_json["edges"].extend(edges)
        original_json["boxes"].append(boxes)
    return original_json
        
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