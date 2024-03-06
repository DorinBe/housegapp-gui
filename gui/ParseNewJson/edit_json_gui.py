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
RESET = '\033[0m'  # Reset to default color
DEBUG = True

edge_map={}
room_map = {}
ed_rm_list = []
reorganized_json={}
original_json = {}
 
edge_selection = False
room_selection = False
units = 1  # pixels

start_x = start_y = current_edge = current_rectangle = None
drag_mode = None  # 'first', 'second', or None

root=0
canvas =  tkinter.Canvas
combobox = tkinter.ttk.Combobox

selected_edge = tkinter.StringVar

MAX_X = 0
MAX_Y = 0

def init_gui(main_frame, width, height, _original_json, _reorganized_json, _root):
    """originally added for implementing the is_inner_room feature to train model to output inner rooms"""

    global canvas, combobox, MAX_X, MAX_Y, original_json, reorganized_json,selected_edge
    MAX_X = width
    MAX_Y = height
    original_json = _original_json
    reorganized_json = _reorganized_json

    canvas = tkinter.Canvas(main_frame.right_frame, width=width, height=height, bg="white")
    is_inner_room_label = tkinter.Label(main_frame.right_frame, text="is inner room?")
    combobox = tkinter.ttk.Combobox(main_frame.right_frame, values=[True,False,None])
    selected_edge_label = tkinter.Label(main_frame.right_frame, text="Selected edge is in room: ")
    selected_edge = tkinter.StringVar()
    selected_edge_dynamic = tkinter.Label(main_frame.right_frame, textvariable=selected_edge)


    canvas.grid(row=0, column=0, sticky="nswe")
    is_inner_room_label.grid(row=1, column=0, sticky="nswe")
    combobox.grid(row=2, column=0)
    selected_edge_label.grid(row=3, column=0, sticky="nswe")
    selected_edge_dynamic.grid(row=4, column=0, sticky="nswe")

    combobox.bind("<<ComboboxSelected>>", partial(on_combo_change))

    reorganized_json = edit_json.add_is_inner_room(reorganized_json)

    draw_boxes(reorganized_json, _root)
    draw_edges(reorganized_json, _root)

def on_combo_change(event):
    global reorganized_json, canvas

    val = combobox.get()
    reorganized_json["rooms"][int(selected_edge.get())]["is_inner_room"] = val

def move_up(event):
    global current_rectangle
    canvas.move(current_rectangle, 0, -units)  # Move up by 'units' units
    canvas.move(f"label-room-{current_rectangle}", 0, -units)

def move_down(event):
    global current_rectangle
    canvas.move(current_rectangle, 0, units)  # Move down by 10 units
    canvas.move(f"label-room-{current_rectangle}", 0, units)

def move_left(event):
    global current_rectangle
    canvas.move(current_rectangle, -units, 0)  # Move left by 10 units
    canvas.move(f"label-room-{current_rectangle}", -units, 0)

def move_right(event):
    global current_rectangle
    canvas.move(current_rectangle, units, 0)  # Move right by 10 units
    canvas.move(f"label-room-{current_rectangle}", units, 0)

def move_up(event):
    global current_rectangle
    canvas.move(current_rectangle, 0, -units)  # Move up by 10 units
    canvas.move(f"label-room-{current_rectangle}", 0, -units)

def on_canvas_click(event):
    print("Canvas clicked at", event.x, event.y)
    event.widget.focus_set()  # Set focus to the canvas when it's clicked


def draw_boxes(data, _root):
    global edge_selection, room_selection, root
    root = _root
    edge_selection = False
    room_selection = True

    if room_map != {}:
        canvas.itemconfigure("edge", width=0.5, fill="gray")
        canvas.itemconfigure("box", width=2, outline="black")
        canvas.tag_raise("box")
        canvas.tag_raise("label")

        canvas.bind("<1>", on_canvas_click)
        canvas.bind("<Button-1>", partial(on_mouse_down))
        canvas.bind("<B1-Motion>", partial(on_mouse_move))
        canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
        root.bind("<Up>", partial(move_up))
        root.bind("<Down>", partial(move_down))
        root.bind("<Left>", partial(move_left))
        root.bind("<Right>", partial(move_right))
        return

    for room in {**data["rooms"],**data["doors"]}.items():
        room_index = room[0]
        room_type = room[1]["room_type"]
        box = room[1]["boxes"]
        x1, y1, x2, y2 = box
        item_id = canvas.create_rectangle(x1, y1, x2, y2, fill="white", width=2, outline="black", tags=("box",
                                                                                                        f"room_index:{room_index}",
                                                                                                        f"room_type:{room_type}",
                                                                                                        f"{room_type}-{room_index}"))
        room_map[item_id] = box
        x, y = edit_json.calculate_averge_of_box(box)
        canvas.create_text(x, y, text=f"{room_index}", font=("Arial", 10), tags=(f"label-room-{item_id}", "label"))
    
    canvas.bind("<1>", on_canvas_click)
    canvas.bind("<Button-1>", partial(on_mouse_down))
    canvas.bind("<B1-Motion>", partial(on_mouse_move))
    canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
    root.bind("<Up>", partial(move_up))
    root.bind("<Down>", partial(move_down))
    root.bind("<Left>", partial(move_left))
    root.bind("<Right>", partial(move_right))

def on_mouse_down(event):
    global current_rectangle, action_type, start_x, start_y, resize_edge
    item = canvas.find_closest(event.x, event.y)[0]
    tags = canvas.gettags(item)
    if "box" in tags:
        current_rectangle = item
        room_index = tags[3].split(":")[1]
        print(f"Selected box index: {room_index}")

        start_x, start_y = event.x, event.y
        x1, y1, x2, y2 = canvas.coords(current_rectangle)
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
    global current_rectangle, action_type, start_x, start_y, drag_mode, resize_edge

    if current_rectangle and action_type == "move":
        dx, dy = event.x - start_x, event.y - start_y
        canvas.move(current_rectangle, dx, dy)
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

def on_mouse_up(event):
    global current_rectangle, action_type, room_map
    canvas.itemconfig(current_rectangle, outline="black")
    action_type = None

    if current_rectangle:
        new_coords = canvas.coords(current_rectangle)
        tags = canvas.gettags(current_rectangle)
        
        if current_rectangle in room_map:
            room_map[current_rectangle] = new_coords

            for tag in tags:
                if "room_index" in tag:
                    room_index = int(tag.split(":")[1])
                    # update the json with the new coordinates => no need concate newdata to originaldata
                    reorganized_json["rooms"][room_index]["boxes"] = new_coords
                    break


        current_rectangle = None

def draw_edges(data, _root):
    """input: reorganized_data"""
    global edge_selection, room_selection
    edge_selection = True
    room_selection = False
    
    if edge_map != {}:
        canvas.itemconfigure("edge", width=2, fill="black")
        canvas.itemconfigure("box", width=0.5, outline="gray")
        canvas.tag_raise("edge")
        canvas.tag_raise("label")
        canvas.bind("<Button-1>", partial(start_drag))
        canvas.bind("<B1-Motion>", partial(drag))
        canvas.bind("<ButtonRelease-1>", partial(end_drag))
        return

    for room in {**data["rooms"], **data["doors"]}.items():
        room_index = room[0]
        edges = room[1]["edges"]
        box = room[1]["boxes"]
        room_type = room[1]["room_type"]

        for index_in_edge_list,edge in enumerate(edges):
            try:
                x1, y1, x2, y2, room_type, neighbour_room = edge
                item_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge", 
                                                                                          f"{room_type}-{neighbour_room}",
                                                                                          f"room_index:{room_index}",
                                                                                          f"edge_index={index_in_edge_list}"))
                edge_map[item_id] = edge

                if (room_type < 10):
                    x, y = edit_json.calculate_averge_of_box(box)
                    canvas.create_text(x, y, text=f"{room_index}", font=("Arial", 10), tags=(f"label-room-{room_index}", "label"))
            except Exception as e:
                traceback.format_exc(e)

    canvas.bind("<Button-1>", partial(start_drag))
    canvas.bind("<B1-Motion>", partial(drag))
    canvas.bind("<ButtonRelease-1>", partial(end_drag))

def start_drag(event):
    global start_x, start_y, current_edge, drag_mode, selected_edge
    item = canvas.find_closest(event.x, event.y)[0]  # Find the closest item to the click
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

def drag(event):
    global start_x, start_y, current_edge, drag_mode
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
    global current_edge, drag_mode
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
        path = path + '_' + str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + '.json'
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

def on_clear():
    global edge_map, room_map, reorganized_json, edge_selection, room_selection, ed_rm_list
    global start_x, start_y, current_edge, current_rectangle, drag_mode
    global root, canvas, combobox, original_json

    edge_map={}
    room_map = {}
    reorganized_json={}
    original_json = {}
    ed_rm_list = []

    edge_selection = False
    room_selection = False

    start_x = start_y = current_edge = current_rectangle = None
    drag_mode = None  # 'first', 'second', or None

    root=0
    canvas =  tkinter.Canvas
    combobox = ttk.Combobox

    init_gui(root, 800, 600, original_json, reorganized_json)

def get_last_room_index():
    # item_id = list(room_map)[-1]
    # room_index = int(canvas.gettags(item_id)[-1].split('-')[1])
    room_index = list(reorganized_json["rooms"])[-1]+1

    return room_index

def add_box_random(random_box, room_type):
        x1, y1, x2, y2 = random_box
        room_index = get_last_room_index()
        box_id = canvas.create_rectangle(x1, y1, x2, y2, fill="white", width=2, outline="black", 
                                         tags=("box", "random_box", f"{room_type}-{room_index}",
                                               f"room_index:{room_index}",
                                               f"room_type:{room_type}"))
        reorganized_json["room_types"].insert(room_index, int(room_type))
        room_map[box_id] = random_box
        reorganized_json["rooms"].update({
            room_index:{
                "boxes":random_box,
                "edges":[],
                "ed_rm":[],
                "room_type":room_type
            }
        })
        x, y = edit_json.calculate_averge_of_box(random_box)
        canvas.create_text(x, y, text=f"{room_index}", font=("Arial", 10), tags=(f"label-room-{box_id}","random-label", "label"))
    
        canvas.bind("<1>", on_canvas_click)
        canvas.bind("<Button-1>", partial(on_mouse_down))
        canvas.bind("<B1-Motion>", partial(on_mouse_move))
        canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
        root.bind("<Up>", partial(move_up))
        root.bind("<Down>", partial(move_down))
        root.bind("<Left>", partial(move_left))
        root.bind("<Right>", partial(move_right))
        return room_index, room_type

def add_edge_random(random_edges,room_index):
    for edge in random_edges:
        x1, y1, x2, y2, room_type, neighbour_room = edge
        item_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge", 
                                                                                    f"{room_type}-{neighbour_room}",
                                                                                    f"room_index:{get_last_room_index()}"))
        edge_map[item_id] = edge
        reorganized_json["rooms"][room_index]["edges"].append(edge)

    canvas.bind("<Button-1>", partial(start_drag))
    canvas.bind("<B1-Motion>", partial(drag))
    canvas.bind("<ButtonRelease-1>", partial(end_drag))

def add_random_room(room_type, edges_neighbour_room_types, edges_neighbour_room_indexes):
    global ed_rm_list

    edges_room_types = edges_neighbour_room_types.split(",")
    edges_neighbour_room_indexes = edges_neighbour_room_indexes.split(',')
    if edges_room_types[0] == '' or edges_neighbour_room_indexes[0] == '':
        messagebox.showerror("please fill entries", "please fill entries")
        return
    
    random_box = [400,90,450,130]
    room_index, room_type = add_box_random(random_box, room_type)

    random_edges = [[400,90,400,130,room_index, int(edges_room_types[0])],
                    [400,130,450,130,room_index, int(edges_room_types[1])],
                    [450,130,450,90,room_index, int(edges_room_types[2])],
                    [450,90,400,90,room_index, int(edges_room_types[3])]]
    add_edge_random(random_edges,room_index)
    
    reorganized_json["rooms"][room_index]["ed_rm"] = [[room_index, int(edges_neighbour_room_indexes[0])],
                                                            [room_index, int(edges_neighbour_room_indexes[1])],
                                                            [room_index, int(edges_neighbour_room_indexes[2])],
                                                            [room_index, int(edges_neighbour_room_indexes[3])]]


