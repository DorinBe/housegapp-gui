import os
from datetime import datetime
import json
import traceback

"""
servers as bridge between:
1. original data format expected by the model
2. edits of floorplan by the user
this bridge simplifies the edits on the json file

original data format is json with 4 keys, each key has list of lists, each list index from each key are related.
    {
        "room_type"=    [T1, T2, ..., Tn],
        "boxes"=        [[B1], [B2], ..., [Bn]]],
        "edges"=        [[E1], [E2], ..., [En]],
        "ed_rm"=        [[E1], [ER2], ..., [ERn]]
    }

simplified data format is a json where each key is room, and each key has its' 4 lists.
it simplifies interactions of tkinter canvas with data, allowing for easier manipulation.
    {
        "room_types"=[],
        "rooms"=
            {"room_index":
                {"box": [Bi], "edges":[Ei, neigh1, neigh2],"ed_rm":[EDi, neigh1, neigh2]}
        "doors"=
            {"door_index":
                {"box": [Bi], "edges":[Ei, neigh1, neigh2],"ed_rm":[EDi, neigh1, neigh2]}...}
    }
"""

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

def calculate_average_of_box(box):
    """Calculate the average of a box"""
    x_min, y_min, x_max, y_max = box
    return (x_min + x_max) / 2, (y_min + y_max) / 2

def get_simplified_format_json(original_data_format):
    """Receives original data format, outputs simplified data format"""

    original_room_types = original_data_format["room_type"]
    original_boxes = original_data_format["boxes"]
    original_edges = original_data_format["edges"]
    original_ed_rm = original_data_format["ed_rm"]

    simplified_data_format = {"room_types": [],
                "rooms": {},
                "doors":{} }
    
    if len(original_room_types) == 0:
        return simplified_data_format
    
    from_edge_index, to_edge_index = 0,0
    prev_room_index, curr_room_index = 0,0
    simplified_data_format["room_types"].extend(original_room_types)
    for to_edge_index, ed_rm in enumerate(original_ed_rm):

        curr_room_index = ed_rm[0]
        if (prev_room_index != curr_room_index):
            room_or_door_string = original_room_types[prev_room_index]
            room_or_door_string = "rooms" if room_or_door_string < 11 else "doors"
            new_room = {prev_room_index:{"edges": original_edges[from_edge_index:to_edge_index],
                                         "ed_rm": original_ed_rm[from_edge_index:to_edge_index],
                                         "boxes": original_boxes[prev_room_index],
                                         "room_type": original_room_types[prev_room_index]}}
            
            simplified_data_format[f"{room_or_door_string}"].update(new_room)
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
    simplified_data_format[f"{room_or_door_string}"].update(new_room)
    from_edge_index = to_edge_index
    prev_room_index = curr_room_index
    
    return simplified_data_format

def get_original_format_json(simplified_json) -> dict[str, list]:
    """Receives simplified data format, outputs original data format, 
    necessary to feed data to the model after manipulations on the json."""

    original_json = {
        "room_type": [],
        "boxes": [],
        "edges": [],
        "ed_rm": []
    }

    original_json["room_type"].extend(simplified_json["room_types"])

    for room in simplified_json["rooms"].items():
        edges = room[1]["edges"]
        boxes = room[1]["boxes"]
        ed_rm = room[1]["ed_rm"]

        original_json["boxes"].append(boxes)
        original_json["edges"].extend(edges)
        original_json["ed_rm"].extend(ed_rm)
    
    for door in simplified_json["doors"].items():        
        edges = door[1]["edges"]
        boxes = door[1]["boxes"]
        ed_rm = door[1]["ed_rm"]

        original_json["boxes"].append(boxes)
        original_json["edges"].extend(edges)
        original_json["ed_rm"].extend(ed_rm)
        
    return original_json

def save_json(path, original_format_json)->str:
    """returns the path of the saved file."""
    try:
        path = os.path.dirname(path)
        path = os.path.join(path, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.json')
        with open(path, 'a+') as file:
            json.dump(original_format_json, file)
    except Exception as e:
        return traceback.format_exc(e)
    
    return path