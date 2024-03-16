from functools import partial
import tkinter
from tkinter import ttk
from tkinter import messagebox
from ParseNewJson import edit_json
import json
import traceback

# ANSI escape codes
RED = '\033[31m'  # Red text
GREEN = '\033[32m'  # Green text
BLUE = '\033[34m'  # Blue text
YELLOW = '\033[33m'  # Yellow text
RESET = '\033[0m'  # Reset to default color
DEBUG = True

# ************** Variables that should be cleared when clear is clicked  ************** #
room_map = {}
edge_map = {}
ed_rm_list = []
reorganized_json={}
edge_selection = False
room_selection = False
room_edge_selection = False
start_x = start_y = current_edge = current_rectangle = room_index_together = None
drag_mode = None  # 'first', 'second', or None
root=0
canvas =  tkinter.Canvas
combobox = tkinter.ttk.Combobox

# ************** Globals  ************** #
units = 1  # pixels
selected_edge = selected_box = selected_door= tkinter.StringVar
room_type_sv = tkinter.StringVar
neigh_room_indexes_sv = tkinter.StringVar
neigh_room_types_sv = tkinter.StringVar
neigh_door_indexes_sv = tkinter.StringVar
neigh_door_types_sv = tkinter.StringVar

MAX_X = 0
MAX_Y = 0

def init_gui(main_frame, width, height, _reorganized_json, _root, command:str):
    """originally added for implementing the is_inner_room feature to train model to output inner rooms"""

    global canvas, combobox, MAX_X, MAX_Y, reorganized_json,selected_edge
    global room_type_sv, neigh_room_types_sv, neigh_room_indexes_sv, neigh_door_indexes_sv, neigh_door_types_sv
    MAX_X = width-300
    MAX_Y = height-100
    reorganized_json = _reorganized_json
    root = _root
    canvas = tkinter.Canvas(main_frame.right_frame, width=MAX_X, height=MAX_Y, bg="white")
    canvas.grid(row=0, column=0, sticky="nswe")

    if command != "clear":
        room_type_sv = tkinter.StringVar()  
        neigh_door_indexes_sv = tkinter.StringVar()
        neigh_room_types_sv = tkinter.StringVar()
        neigh_room_indexes_sv = tkinter.StringVar()
        neigh_door_types_sv = tkinter.StringVar()
        selected_edge = tkinter.StringVar()
        selected_box = tkinter.StringVar()
        selected_door = tkinter.StringVar()
        draw_boxes(reorganized_json, root)
        draw_edges(reorganized_json, root)
        # reorganized_json = edit_json.add_is_inner_room(reorganized_json)
    canvas.bind("<1>", on_canvas_click)

def on_combo_change(event):
    global reorganized_json, canvas

    val = combobox.get()
    reorganized_json["rooms"][int(selected_edge.get())]["is_inner_room"] = val

def on_canvas_click(event):
    print("Canvas clicked at", event.x, event.y)
    event.widget.focus_set()  # Set focus to the canvas when it's clicked

def draw_boxes(data, _root):
    global edge_selection, room_selection, root, room_edge_selection, room_index_together, canvas
    root = _root
    edge_selection = False
    room_selection = True
    room_edge_selection = False
    room_index_together = None

    if room_map != {}:
        canvas.itemconfigure("edge", width=0.5, fill="gray")
        canvas.itemconfigure("box", width=2, outline="black")
        canvas.tag_raise("box")
        canvas.tag_raise("label")
        canvas.tag_lower("edge")

        canvas.bind("<1>", on_canvas_click)
        canvas.bind("<Button-1>", partial(on_mouse_down))
        canvas.bind("<B1-Motion>", partial(on_mouse_move))
        canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
        return

    for room in {**data["rooms"],**data["doors"]}.items():
        room_index = room[0]
        room_type = room[1]["room_type"]
        box = room[1]["boxes"]
        x1, y1, x2, y2 = box
        item_id = canvas.create_rectangle(x1, y1, x2, y2, fill="white", width=2, outline="black", tags=("box",
                                                                                                        f"room_index:{room_index}",
                                                                                                        f"room_type:{room_type}"))
        room_map[item_id] = box
        x, y = edit_json.calculate_averge_of_box(box)
        label_id = canvas.create_text(x, y, text=f"{room_index}", font=("Arial", 8), tags=("label",
                                                                                            f"label_room_index:{room_index}",
                                                                                            f"label_room_type:{room_type}",
                                                                                            f"label_item_id:{item_id}"))
        canvas.tag_unbind(label_id, '<Button-1>')  # Unbind left mouse click events from the item
        
    
    canvas.bind("<1>", on_canvas_click)
    canvas.bind("<Button-1>", partial(on_mouse_down))
    canvas.bind("<B1-Motion>", partial(on_mouse_move))
    canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))


def draw_edges(data, _root):
    """input: reorganized_data"""
    global edge_selection, room_selection, room_edge_selection, room_index_together, canvas
    edge_selection = True
    room_selection = False
    room_edge_selection = False
    room_index_together = None
    
    if edge_map != {}:
        canvas.itemconfigure("edge", width=2, fill="black")
        canvas.itemconfigure("box", width=0.5, outline="gray")
        canvas.tag_raise("edge")
        canvas.tag_raise("label")
        canvas.tag_lower("box")
        canvas.bind("<Button-1>", partial(start_drag))
        canvas.bind("<B1-Motion>", partial(drag))
        canvas.bind("<ButtonRelease-1>", partial(end_drag))
        return

    for room in {**data["rooms"], **data["doors"]}.items():
        room_index = room[0]
        edges = room[1]["edges"]
        box = room[1]["boxes"]
        room_type = room[1]["room_type"]

        is_door = True if room_type > 11 else False
        for index_in_edge_list,edge in enumerate(edges):
            try:
                x1, y1, x2, y2, room_type, neighbour_room = edge
                item_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge",
                                                                                          f"edge_room_index:{room_index}",
                                                                                          f"edge_is_door:{is_door}"))
                edge_map[item_id] = edge                    
            except Exception as e:
                traceback.format_exc(e)

    canvas.bind("<Button-1>", partial(start_drag))
    canvas.bind("<B1-Motion>", partial(drag))
    canvas.bind("<ButtonRelease-1>", partial(end_drag))

def on_mouse_down(event):
    global current_rectangle, action_type, start_x, start_y, resize_edge, canvas
    global room_index_together, room_edge_selection

    item = canvas.find_closest(event.x, event.y)[0]
    tags = canvas.gettags(item)
    if "box" in tags:
        current_rectangle = item
        room_index = tags[1].split(":")[1]
        if room_edge_selection == True:
            room_index_together = int(room_index)
            canvas.itemconfigure("edge", width=0.5, fill="black")
            canvas.itemconfigure("box", width=2, outline="black")
            canvas.itemconfig(current_rectangle, outline="green")
            canvas.itemconfigure(f"edge_room_index:{room_index}", fill="green")
    elif "edge" in tags:
        is_door = bool(tags[3].split(":")[-1])
        if is_door == True:
            room_index = tags[1].split(":")[-1]
            current_rectangle = canvas.find_withtag(f"room_index:{room_index}")
            room_index_together = int(room_index)
            canvas.itemconfigure("edge", width=0.5, fill="black")
            canvas.itemconfigure("box", width=2, outline="black")
            canvas.itemconfig(current_rectangle, outline="green")
            canvas.itemconfigure(f"edge_room_index:{room_index}", fill="green")

    start_x, start_y = event.x, event.y
    try:
        x1, y1, x2, y2 = canvas.coords(current_rectangle)
    except:
        print(f"{RED}Error in on_mouse_down:current_rectangle: {current_rectangle}")
    edge_margin = 5  # pixels

    on_left_edge = abs(x1 - event.x) < edge_margin
    on_right_edge = abs(x2 - event.x) < edge_margin
    on_top_edge = abs(y1 - event.y) < edge_margin
    on_bottom_edge = abs(y2 - event.y) < edge_margin

    if on_left_edge:
        resize_edge = "left"
    elif on_right_edge:
        resize_edge = "right"
    elif on_top_edge:
        resize_edge = "top"
    elif on_bottom_edge:
        resize_edge = "bottom"
    else:
        resize_edge = None

    action_type = "resize" if resize_edge else "move"
    canvas.itemconfig(current_rectangle, outline="green")
    canvas.focus_set()

def on_mouse_move(event):
    global start_x, start_y,current_rectangle, drag_mode
    global resize_edge, canvas, action_type, room_index_together
    dx,dy = 0,0

    if current_rectangle and action_type == "move":
        dx, dy = event.x - start_x, event.y - start_y
        canvas.move(current_rectangle, dx, dy)
        canvas.move(f"label_item_id:{current_rectangle}", dx, dy)
    elif current_rectangle and action_type == "resize":
        x1, y1, x2, y2 = canvas.coords(current_rectangle)

        if resize_edge == "left":
            x1 = event.x
        elif resize_edge == "right":
            x2 = event.x
        if resize_edge == "top":
            y1 = event.y
        elif resize_edge == "bottom":
            y2 = event.y

        min_size = 10
        new_width = max(x2 - x1, min_size)
        new_height = max(y2 - y1, min_size)

        if new_width > min_size:
            if resize_edge == "left":
                x1 = x2 - new_width
            else:
                x2 = x1 + new_width
        if new_height > min_size:
            if resize_edge == "top":
                y1 = y2 - new_height
            else:
                y2 = y1 + new_height

        canvas.coords(current_rectangle, x1, y1, x2, y2)

    start_x, start_y = event.x, event.y

    return dx,dy

def update_new_coords():
    global current_rectangle, action_type, room_map, canvas, room_index_together
    global room_edge_selection, reorganized_json

    if current_rectangle:
        new_coords = canvas.coords(current_rectangle)
        tags = canvas.gettags(current_rectangle)
        
        if current_rectangle in room_map:
            room_map[current_rectangle] = new_coords

            room_type = int(tags[2].split(":")[1])
            rooms_or_doors = "doors" if room_type > 11 else "rooms"
            room_index = int(tags[1].split(":")[1])
            reorganized_json[rooms_or_doors][room_index]["boxes"] = new_coords

        if room_edge_selection:
            update_edges_coords = canvas.find_withtag(f"edge_room_index:{room_index_together}")
            for i, edge in enumerate(update_edges_coords):
                new_coords = canvas.coords(edge)
                reorganized_json[rooms_or_doors][room_index_together]["edges"][i][:4] = new_coords

def on_mouse_up(event):
    global current_rectangle, action_type, room_map, canvas, room_index_together
    global room_edge_selection, reorganized_json

    canvas.itemconfig(current_rectangle, outline="black")
    action_type = None

    """added this code to update_new_coords()"""
    if current_rectangle:
        new_coords = canvas.coords(current_rectangle)
        tags = canvas.gettags(current_rectangle)
        
        if current_rectangle in room_map:
            room_map[current_rectangle] = new_coords

            room_type = int(tags[2].split(":")[1])
            rooms_or_doors = "doors" if room_type > 11 else "rooms"
            room_index = int(tags[1].split(":")[1])
            reorganized_json[rooms_or_doors][room_index]["boxes"] = new_coords

        if room_edge_selection:
            update_edges_coords = canvas.find_withtag(f"edge_room_index:{room_index_together}")
            for i, edge in enumerate(update_edges_coords):
                new_coords = canvas.coords(edge)
                reorganized_json[rooms_or_doors][room_index_together]["edges"][i][:4] = new_coords

        # current_rectangle = None


def start_drag(event):
    global start_x, start_y, current_edge, drag_mode, selected_edge, canvas
     
    item = canvas.find_closest(event.x, event.y)[0]  # Find the closest item to the click
    print(f"closeset item: {item}")
    tags = canvas.gettags(item)
    if "edge" in tags:
        start_x, start_y = event.x, event.y
        current_edge = item
        for tag in tags:
            if "room_index" in tag:
                room_index = tag.split(":")[-1]
                selected_edge.set(room_index)
                break

        canvas.itemconfig(current_edge, fill="green", width=2)
        line_coords = canvas.coords(current_edge)
        # Determine if the click is near an endpoint
        drag_mode = is_close_to_endpoint(start_x, start_y, line_coords)

def drag(event, _dx=None,_dy=None):
    global start_x, start_y, current_edge, drag_mode
    global room_index_together, room_edge_selection, canvas

    if room_edge_selection:
        canvas.move(f"edge_room_index:{room_index_together}", _dx, _dy)

    if current_edge:
        dx = event.x - start_x
        dy = event.y - start_y

        if drag_mode == 'first':  # Dragging the first endpoint
            coords = canvas.coords(current_edge)
            canvas.coords(current_edge, event.x, event.y, coords[2], coords[3])
        elif drag_mode == 'second':  # Dragging the second endpoint
            coords = canvas.coords(current_edge)
            canvas.coords(current_edge, coords[0], coords[1], event.x, event.y)
        else:  # Moving the entire edge
            canvas.move(current_edge, dx, dy)

        start_x, start_y = event.x, event.y

def end_drag(event):
    global current_edge, drag_mode, canvas
    if current_edge:
        canvas.itemconfig(current_edge, fill="black", width=2)
        new_coords = canvas.coords(current_edge)
        tags = canvas.gettags(current_edge)
        if current_edge in edge_map:
            edge_map[current_edge][:4] = new_coords

            for tag in tags:
                if "room_index" in tag:
                    room_index = int(tag.split(":")[1])
                    for _tag in tags:
                        if "edge_index" in _tag:
                            edge_index = int(_tag.split("=")[-1])
                            # update edges directly to the reorganized_json no need to concate newdata to originaldata
                            reorganized_json["rooms"][room_index]["edges"][edge_index][:4] = new_coords
                    break

        current_edge = None
        drag_mode = None

def dump_boxes(path, fixed_json):
    from datetime import datetime
    try:
        path = path + '_' + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.json'
        with open(path, 'a+') as file:
            json.dump(fixed_json, file)
    except Exception as e:
        return traceback.format_exc(e)
    return "File saved as " + path

def output_newdata_to_original_format_with_is_inner_room(data, _root, reorganized_json):
    new_data = concate_newdata_to_originaldata(data, _root)
    new_data["is_inner_room"] = []
    # new_data["is_inner_room"] = reorganized_json["is_inner_room"]

    # get the "is_inner_room" from the reorganized_json from each room
    for room_index, items in reorganized_json["rooms"].items():
        new_data["is_inner_room"].append(items["is_inner_room"])

    return new_data

def concate_newdata_to_originaldata(data, _root):
    """ Input: original data in original format
        Output: updated data in original format """
    newdata = { "room_type": [], "boxes": [], "edges":[], "ed_rm":[]}

    newdata["room_type"] = data["room_type"]
    newdata["boxes"] = [value for value in room_map.values()]
    newdata["edges"] = [value for value in edge_map.values()]
    newdata["ed_rm"] = data["ed_rm"]
    newdata["ed_rm"].append(ed_rm_list)

    return newdata

def is_close_to_endpoint(x, y, line_coords, threshold=10):
    x1, y1, x2, y2 = line_coords
    near_first_endpoint = (x - x1)**2 + (y - y1)**2 <= threshold**2
    near_second_endpoint = (x - x2)**2 + (y - y2)**2 <= threshold**2
    if near_first_endpoint:
        return 'first'
    elif near_second_endpoint:
        return 'second'
    return None

def validate_data(reorganized_json):
    for room_index, items in reorganized_json["rooms"].items():
        edges, ed_rm, boxes,room_type = items["edges"], items["ed_rm"], items["boxes"], items["room_type"]
        for i, edge in enumerate(edges):
            if not edit_json.is_edge_inside_box(edge, boxes):
                print(f"Edge {edge} not found in any box")
                fixed_edge = edit_json.fix_difference_between_edge_to_box(edge, boxes)
                reorganized_json['rooms'][room_index]['edges'][i] = fixed_edge
                fixed_edge=None
    return reorganized_json

def on_close(originaldata, path, message_label_middle, root, reorganized_data):
    """input: original data format {"room_type"=[3,3,1,...], 
                                    "boxes"=[[58.0, 78.0, 130.0, 122.0],...], 
                                    "edges"=[[58.0, 122.0, 130.0, 122.0, 3, 1],...], # where 3 is current room_type and 1 is neighbour_room_type
                                    "ed_rm"=[[0], [0, 2],....]} # where 0 is corresponding room_index and 2 is neighbour_index
    """
    global reorganized_json
    # check all items on canvas 
    if not edge_map:
        draw_edges(reorganized_data, root)
    if not room_map:
        draw_boxes(reorganized_data, root)

    """already updated reorganized_json with the new data in previous stages (end_drag, on_mouse_up)"""
    # newdata = concate_newdata_to_originaldata(originaldata, root)
    # reorganized_json = edit_json.reorganize_json(reorganized_json)
    original_format_json = edit_json.deorganize_format(reorganized_json)
    new_path = dump_boxes(path, original_format_json)
    message_label_middle.config(text=new_path)

def on_clear(main_frame):
    global edge_map, room_map, reorganized_json, edge_selection, room_selection, ed_rm_list
    global start_x, start_y, current_edge, current_rectangle, drag_mode
    global root, canvas, combobox, room_edge_selection, room_index_together

    edge_map={}
    room_map = {}
    reorganized_json={"room_types":[], "rooms":{}, "doors":{}}
    ed_rm_list = []

    edge_selection = False
    room_selection = False
    room_edge_selection = False

    start_x = start_y = current_edge = current_rectangle = room_index_together = None
    drag_mode = None  # 'first', 'second', or None

    root=0
    canvas =  tkinter.Canvas
    combobox = ttk.Combobox

    init_gui(main_frame, 800, 600, reorganized_json, root, "clear")

def get_last_room_index():
    if len(list(reorganized_json["rooms"])) == 0:
        room_index = 0
    else:
        room_index = list(reorganized_json["rooms"])[-1]+1
    return room_index

def add_box_random(random_box, room_or_door_type, room_or_door:str, room_index):
        global canvas, reorganized_json, room_map

        x1, y1, x2, y2 = random_box
        if room_or_door == "room":
            new_index = room_index
            new_index_for_label = new_index
        else:
            new_index = room_index
            new_index_for_label = new_index + list(reorganized_json["rooms"])[-1]
        room_type = int(room_or_door_type)
        box_id = canvas.create_rectangle(x1, y1, x2, y2, fill="white", width=2, outline="black", 
                                         tags=("box", "random_box"
                                            f"room_index:{room_index}",
                                            f"room_type:{room_type}"))
        reorganized_json["room_types"].insert(new_index, room_type)

        room_map[box_id] = random_box #TODO is it also for doors? 
        x, y = edit_json.calculate_averge_of_box(random_box)
        label_id=canvas.create_text(x, y, text=f"{new_index}", font=("Arial", 8), tags=("label",
                                                                                        "random-label",
                                                                                        f"label_room_index:{new_index}",
                                                                                        f"label_room_type:{room_type}",
                                                                                        f"label_item_id:{box_id}"))
        canvas.tag_unbind(label_id, '<Button-1>')  # Unbind left mouse click events from the item
    
        canvas.bind("<1>", on_canvas_click)
        canvas.bind("<Button-1>", partial(on_mouse_down))
        canvas.bind("<B1-Motion>", partial(on_mouse_move))
        canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
        return new_index, room_or_door_type

def add_edge_random(random_edges,room_index, rooms_or_doors):
    global canvas, reorganized_json, edge_map
    for edge in random_edges:
        x1, y1, x2, y2, room_type, neighbour_room = edge
        is_door = True if room_type > 11 else False
        item_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge", 
                                                                                  "random_edge",
                                                                                    f"edge_room_index:{room_index}",
                                                                                    f"edge_is_door:{is_door}"))
        edge_map[item_id] = edge
        reorganized_json[rooms_or_doors][room_index]["edges"].append(edge)

def change_tag_to_new_index(old_tag, new_tag):
    global canvas
    canvas.addtag_withtag(new_tag, old_tag)
    canvas.dtag(new_tag, old_tag)

def increment_doors_index(new_room_index, door_indexes):
    """is called only when adding new room because room is added 
    to the middle of the json and the doors indexes are all after the rooms."""
    if reorganized_json["doors"] == {}:
        last_door_index = 1
    else:
        last_door_index = list(reorganized_json["doors"])[-1]+1
    combined_ed_list = []
    for value in {**reorganized_json["rooms"], **reorganized_json["doors"]}.values():
        for _list in value["ed_rm"]:
            combined_ed_list.append(_list)
        
    for ed_rm in combined_ed_list:
        if ed_rm[0] >= new_room_index:
            change_tag_to_new_index(f"room_index:{ed_rm[0]}", f"room_index:{ed_rm[0]+1}")
            change_tag_to_new_index(f"edge_room_index:{ed_rm[0]}", f"edge_room_index:{ed_rm[0]+1}")
            items_with_old_tag = canvas.find_withtag(f"label_room_index:{ed_rm[0]}")
            for item in items_with_old_tag:
                    canvas.itemconfig(item, text=f"{ed_rm[0]+1}")
            ed_rm[0] = ed_rm[0]+1
            try:
                if ed_rm[1] >= new_room_index:
                    ed_rm[1] = ed_rm[1]+1
            except: # not all doors have 2nd index
                pass 

    new_doors_dict = {}

    for key,val in reorganized_json["doors"].items():
        new_doors_dict[key+1] = val

    del reorganized_json["doors"]
    reorganized_json["doors"] = new_doors_dict

    for i,value in enumerate(door_indexes):
        if value != 'N':
            door_indexes[i] = str(int(value)+1)

def find_dir(index):
    index = index % 4
    match (index):
        case 0:
            return 2
        case 1:
            return 3
        case 2:
            return 0
        case 3:
            return 1

def update_edges_and_ed_rm_to_add_random_room(room_index, room_type, room_types, room_indexes, door_indexes, door_types):
    """Update ed_rm and edges according to user's input when adding a new room.
    This algorithm actually works if the neighbours are doors or rooms because only neighbours are being updated.
    so if a door neighbour is updated, then the door's neighbour will be a room V
    and if a room neighbour is updates, then the room's neighbour will be a room V
    function is not changed for an addition of a room. pretty tricky concept."""
    global reorganized_json

    for i, index in enumerate(room_indexes):
        if index == 'N' or index == 'n':
            continue
        index = int(index)
        type = int(room_types[i])

        dir=find_dir(i)
        reorganized_json["rooms"][index]["ed_rm"][dir] = [index, room_index]
        reorganized_json["rooms"][index]["edges"][dir][5] = room_type 

    for i, index in enumerate(door_indexes):
        if index == 'N' or index == 'n':
            continue
        index = int(index)
        type = int(door_types[i])

        dir=find_dir(i)
        reorganized_json["doors"][index]["ed_rm"][dir] = [index, room_index]
        reorganized_json["doors"][index]["edges"][dir][5] = room_type 

def append_ed_rm_list(room_index, neighbour_room_indexes):
    res = []

    for i, neigh_index in enumerate(neighbour_room_indexes):
        if neigh_index == 'N':
            res.append([int(room_index)])
        else:
            res.append([room_index, int(neigh_index)])
    return res

def if_neighbour_doors_increment_their_index(neighbour_types, neighbour_edges):
    for i, _type in enumerate(neighbour_types):
        if _type is None:
            continue
        _type = int(_type)
        if _type > 10: # is room
            neighbour_types[i] = neighbour_types[i]+1
            neighbour_edges[i] = neighbour_edges[i]+1

def add_random_door(direction):
    global ed_rm_list, room_type_sv

    try:
        door_type = int(room_type_sv.get())
        room_indexes = neigh_room_indexes_sv.get().split(",")
        room_types = neigh_room_types_sv.get().split(",")
    except:
        pass

    x_threshold = 7
    y_threshold = 2
    x=400
    y=90

    if room_types == ['']:
        room_types = ['0','0','0','0']

    if direction == "horizontal":
        rd = random_door = [x,y,x+x_threshold,y+y_threshold]
        random_edges = [[rd[0],rd[1],rd[0],rd[3],door_type, int(room_types[0])],
                        [rd[0],rd[3],rd[2],rd[3],door_type, int(room_types[1])],
                        [rd[2],rd[3],rd[2],rd[1],door_type, int(room_types[2])],
                        [rd[2],rd[1],rd[0],rd[1],door_type, int(room_types[3])]]
    else:
        rd = random_door = [x,y,x+y_threshold,y+x_threshold]
        random_edges = [[rd[0],rd[1],rd[0],rd[3],door_type, int(room_types[0])],
                        [rd[0],rd[3],rd[2],rd[3],door_type, int(room_types[1])],
                        [rd[2],rd[3],rd[2],rd[1],door_type, int(room_types[2])],
                        [rd[2],rd[1],rd[0],rd[1],door_type, int(room_types[3])]]

    # a door's index is num of rooms+doors+1
    # but at the end, a new order is formed so in the begining "doors" starts from key 1
    if list(reorganized_json["doors"]) == []:
        door_index = 1
    else:
        door_index = list(reorganized_json["doors"])[-1]+1
    
    try:
        reorganized_json["doors"].update({door_index:{"boxes":random_door, "edges":[], "ed_rm":[], 
                                                      "room_type":room_type_sv.get()}})
    except KeyError as e:
        if str(e) == door_index:
            reorganized_json["doors"][door_index] = {"boxes":random_door,"edges":[],"ed_rm":[],
                                                     "room_type":room_type_sv.get()}



    if room_types[0] == '' or room_indexes[0] == '':
        messagebox.showerror("please fill entries", "no neighbors were added in entries")

    # update_edges_and_ed_rm_to_add_random_door(door_index, door_type, room_types, room_indexes)
    add_box_random(random_door, door_type, "door", door_index)


    add_edge_random(random_edges,door_index,"doors")

    if room_indexes == ['']:
        room_indexes = ['N','N','N','N']
    restoappend = append_ed_rm_list(door_index, room_indexes)
    for item in restoappend:
        try:
            reorganized_json["doors"][door_index]["ed_rm"].append(item)
        except KeyError as e:
            reorganized_json["doors"][door_index]["ed_rm"] = [item]


def add_random_room():
    global ed_rm_list

    random_box = [400,90,450,130]

    room_index = get_last_room_index()

    room_type = int(room_type_sv.get())
    room_indexes = neigh_room_indexes_sv.get().split(",")
    room_types = neigh_room_types_sv.get().split(",")
    door_indexes = neigh_door_indexes_sv.get().split(",")
    door_types = neigh_door_types_sv.get().split(",")

    try:
        reorganized_json["rooms"].update({room_index:{"boxes":random_box, "edges":[], "ed_rm":[], 
                                                      "room_type":room_type}})
    except KeyError as e:
        if str(e) == room_index:
            reorganized_json["rooms"][room_index] = {"boxes":random_box,"edges":[],"ed_rm":[],
                                                     "room_type":room_type}

    increment_doors_index(room_index, door_indexes)
    try:
        if room_types[0] != '':
            update_edges_and_ed_rm_to_add_random_room(room_index, room_type, room_types, room_indexes, door_indexes, door_types)
    except:
        pass
    add_box_random(random_box, room_type, "room", room_index)

    if room_types == ['']:
        room_types = ['0','0','0','0']
    random_edges = [[400,90,400,130,room_type, int(room_types[0])],
                    [400,130,450,130,room_type, int(room_types[1])],
                    [450,130,450,90,room_type, int(room_types[2])],
                    [450,90,400,90,room_type, int(room_types[3])]]
    add_edge_random(random_edges,room_index,"rooms")

    if room_indexes == ['']:
        room_indexes = ['N','N','N','N']
    restoappend = append_ed_rm_list(room_index, room_indexes)
    for item in restoappend:
        try:
            reorganized_json["rooms"][room_index]["ed_rm"].append(item)
        except KeyError as e:
            reorganized_json["rooms"][room_index]["ed_rm"] = [item]

def on_mouse_down_together(event):
    on_mouse_down(event)

def on_mouse_move_together(event):
    global room_index_together
    dx,dy = on_mouse_move(event)
    drag(event,dx,dy)

def on_mouse_up_together(event):
    on_mouse_up(event)
    end_drag(event)
    
def move_up(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, 0, -units)  # Move up by 'units' units
    canvas.move(f"label_room_index:{room_index_together}", 0, -units)
    canvas.move(f"edge_room_index:{room_index_together}", 0, -units)
    update_new_coords()

def move_down(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, 0, units)  # Move down by 10 units
    canvas.move(f"label_room_index:{room_index_together}", 0, units)
    canvas.move(f"edge_room_index:{room_index_together}", 0, units)
    update_new_coords()

def move_left(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, -units, 0)  # Move left by 10 units
    canvas.move(f"label_room_index:{room_index_together}", -units, 0)
    canvas.move(f"edge_room_index:{room_index_together}", -units, 0)
    update_new_coords()

def move_right(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, units, 0)  # Move right by 10 units
    canvas.move(f"label_room_index:{room_index_together}", units, 0)
    canvas.move(f"edge_room_index:{room_index_together}",  units, 0)
    update_new_coords()

def move_edges_and_boxes_together():
    global room_edge_selection, canvas
    room_edge_selection = True
    canvas.bind("<1>", on_canvas_click)
    canvas.bind("<Button-1>", partial(on_mouse_down_together))
    canvas.bind("<B1-Motion>", partial(on_mouse_move_together))
    canvas.bind("<ButtonRelease-1>", partial(on_mouse_up_together))
    canvas.bind("<Up>", partial(move_up))
    canvas.bind("<Down>", partial(move_down))
    canvas.bind("<Left>", partial(move_left))
    canvas.bind("<Right>", partial(move_right))


