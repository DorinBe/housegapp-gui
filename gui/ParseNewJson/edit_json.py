from datetime import datetime
import json
import traceback

# First three functions were meant fix the edge selection problem depicted in edit_json_gui.py

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
    """Function needs more refinement before it can be used."""
    replacedX = replacedY = False
    ex1, ey1, ex2, ey2 = edge[:4]
    bx1, by1, bx2, by2 = box
    room_index = edge[4]
    room_neighbor_index = edge[5]

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
        print(f"ex1 {ex1} < bx1 {bx1}, differencing to ex1=bx1 {bx1}")
        ex1 = bx1
    if ex2>bx2:
        print(f"ex2 {ex2} > bx2 {bx2}, differencing to ex2=bx2 {bx2}")
        ex2 = bx2
    if ey1<by1:
        print(f"ey1 {ey1} < by1 {by1}, differencing to ey1=by1 {by1}")
        ey1 = by1
    if ey2>by2:
        print(f"ey2 {ey2} > by2 {by2}, differencing to ey2=by2 {by2}")
        ey2 = by2

    if replacedX:
        temp = ex1
        ex1 = ex2
        ex2 = temp
    if replacedY:
        temp = ey1
        ey1 = ey2
        ey2 = temp

    return ex1, ey1, ex2, ey2,room_index, room_neighbor_index

def find_edge_in_boxes(edge, boxes):
    for box in boxes:
        if is_edge_inside_box(edge, box):
            return box
    return None

def calculate_average_of_box(box):
    """Calculate the average of a box"""
    x_min, y_min, x_max, y_max = box
    return (x_min + x_max) / 2, (y_min + y_max) / 2

def reorganize_json(data):
    """Reorganize the original data format {"room_type"=[], "boxes"=[], ...} to a simpler format 
    {
        "room_types"=[],
        "rooms"={"room_index:{"box":[],"edges":[],"ed_rm":[]},...}
        "doors"={"door_index":{"box":[],"edges":[],"ed_rm":[]}...}
    }
    Returns the reorganized_data
    """

    original_room_types = data["room_type"]
    original_boxes = data["boxes"]
    original_edges = data["edges"]
    original_ed_rm = data["ed_rm"]

    new_json = {"room_types": [],
                "rooms": {},
                "doors":{} }
    
    if len(original_room_types) == 0:
        return new_json
    
    from_edge_index, to_edge_index = 0,0
    prev_room_index, curr_room_index = 0,0
    new_json["room_types"].extend(original_room_types)
    for to_edge_index, ed_rm in enumerate(original_ed_rm):

        curr_room_index = ed_rm[0]
        if (prev_room_index != curr_room_index):
            room_or_door_string = original_room_types[prev_room_index]
            room_or_door_string = "rooms" if room_or_door_string < 11 else "doors"
            new_room = {prev_room_index:{"edges": original_edges[from_edge_index:to_edge_index],
                                         "ed_rm": original_ed_rm[from_edge_index:to_edge_index],
                                         "boxes": original_boxes[prev_room_index],
                                         "room_type": original_room_types[prev_room_index]}}
            
            new_json[f"{room_or_door_string}"].update(new_room)
            from_edge_index = to_edge_index
            prev_room_index = curr_room_index

    try:
        room_or_door_string = original_room_types[prev_room_index]
        room_or_door_string = "rooms" if room_or_door_string < 11 else "doors"
        new_room = {prev_room_index:{"edges": original_edges[from_edge_index:to_edge_index+1],
                                        "ed_rm": original_ed_rm[from_edge_index:to_edge_index+1],
                                        "boxes": original_boxes[prev_room_index],
                                        "room_type": original_room_types[prev_room_index]}}
    except:
        print("adding last room failed.")
    new_json[f"{room_or_door_string}"].update(new_room)
    from_edge_index = to_edge_index
    prev_room_index = curr_room_index
    
    return new_json

def deorganize_format(reorganized_json):
    """ Input:  updated data in reorganized format
        Output: updated data in original format"""

    original_json = {
        "room_type": [],
        "boxes": [],
        "edges": [],
        "ed_rm": []
    }

    original_json["room_type"].extend(reorganized_json["room_types"])

    for room in reorganized_json["rooms"].items():
        edges = room[1]["edges"]
        boxes = room[1]["boxes"]
        ed_rm = room[1]["ed_rm"]

        original_json["boxes"].append(boxes)
        original_json["edges"].extend(edges)
        original_json["ed_rm"].extend(ed_rm)
    
    for door in reorganized_json["doors"].items():        
        edges = door[1]["edges"]
        boxes = door[1]["boxes"]
        ed_rm = door[1]["ed_rm"]

        original_json["boxes"].append(boxes)
        original_json["edges"].extend(edges)
        original_json["ed_rm"].extend(ed_rm)
        
    return original_json

def dump_boxes(path, fixed_json)->str:
    """returns the path of the saved file."""
    try:
        import os     
        path = os.path.dirname(path)
        path = os.path.join(path, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.json')
        with open(path, 'a+') as file:
            json.dump(fixed_json, file)
    except Exception as e:
        return traceback.format_exc(e)
    
    return path