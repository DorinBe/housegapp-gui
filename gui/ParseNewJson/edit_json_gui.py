import tkinter
from tkinter import ttk, messagebox, StringVar, Canvas
import os
from functools import partial
from ParseNewJson import edit_json
import traceback
from globals import room_id_to_color, room_name_to_id
import globals as g 
from GUI.Utils import find_tag


from gui_path import env_path
from Assets.Extraction.extraction import extraction_path, dump_path

# ************** Variables that should be cleared when clear is clicked  ************** #
room_map = {}
edge_map = {}
ed_rm_list = []
reorganized_json={}

edge_selection = False
current_edge = None

room_selection = False
current_rectangle = None

room_edge_selection = False
room_index_together = None 
"""room_index_together specifies selected index when using 'room_edge_selection' mode """

start_x = None
start_y = None
drag_mode = None  # 'first', 'second', or None
canvas =  tkinter.Canvas
combobox = tkinter.ttk.Combobox

# ************** Globals  ************** #
units = 1  # pixels

room_type_sv    = StringVar
neigh_room_indexes_sv   = StringVar
neigh_room_types_sv     = StringVar
neigh_door_indexes_sv   = StringVar
neigh_door_types_sv     = StringVar
selected_index_sv  = StringVar
selected_type_sv   = StringVar

MAX_X = 0
MAX_Y = 0

def init_gui(edit_json_frame, width, height, _reorganized_json, command:str):
    """originally added for implementing the is_inner_room feature to train model to output inner rooms"""

    global canvas, combobox, MAX_X, MAX_Y, reorganized_json,selected_edge
    global room_type_sv, neigh_room_types_sv, neigh_room_indexes_sv, neigh_door_indexes_sv, neigh_door_types_sv
    global selected_index_sv, selected_type_sv

    on_clear(edit_json_frame, True)

    MAX_X = width-500
    MAX_Y = height-100
    reorganized_json = _reorganized_json

    canvas = tkinter.Canvas(edit_json_frame, width=MAX_X, height=MAX_Y, bg="white")
    canvas.grid(row=0, column=0, sticky="nswe")

    if command != "clear":
        room_type_sv = tkinter.StringVar()  
        neigh_door_indexes_sv = tkinter.StringVar()
        neigh_room_types_sv = tkinter.StringVar()
        neigh_room_indexes_sv = tkinter.StringVar()
        neigh_door_types_sv = tkinter.StringVar()
        selected_edge = tkinter.StringVar()
        selected_index_sv = tkinter.StringVar()
        selected_type_sv = tkinter.StringVar()

        draw_boxes(reorganized_json)
        draw_edges(reorganized_json)

def draw_rectangle_and_label(canvas:Canvas, x1:float, y1:float, x2:float, y2:float, outline_color:str, box_index:int, box_type:int) -> int:
    """Input: canvas: canvas to draw on, 
    x1,y1,x2,y2: coordinates of the box,
    outline_color: outline colors of the box,
    box_index: index of the room or door,
    box_type: type of the box room or door (Living Room, Front Door, etc.)
    Returns the item_id of the rectangle drawn on the canvas."""
    box_id = canvas.create_rectangle(x1, y1, x2, y2, fill=outline_color, width=2, outline="black", tags=("box",
                                                                                                        f"room_index:{box_index}",
                                                                                                        f"room_type:{box_type}"))
    x, y = edit_json.calculate_average_of_box(box=(x1, y1, x2, y2))
    canvas.create_text(x, y, text=f"{box_index}", font=("Arial", 8), tags=("label",
                                                                            f"label_box_index:{box_index}",
                                                                            f"label_box_type:{box_type}",
                                                                            f"label_box_id:{box_id}"))
    return box_id

def draw_boxes(data):
    global edge_selection, room_selection, room_edge_selection, room_index_together, canvas
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

        canvas.bind("<Button-1>", partial(on_mouse_down))
        canvas.bind("<B1-Motion>", partial(on_mouse_move))
        canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
        return

    for room in {**data["rooms"],**data["doors"]}.items():
        room_index = room[0]
        room_type = room[1]["room_type"]
        room_color = room_id_to_color(room_type)
        
        box = room[1]["boxes"]
        x1, y1, x2, y2 = box
        item_id = draw_rectangle_and_label(canvas, x1, y1, x2, y2, room_color, room_index, room_type)
        room_map[item_id] = box
        x, y = edit_json.calculate_average_of_box(box)
        
    
    canvas.bind("<Button-1>", partial(on_mouse_down))
    canvas.bind("<B1-Motion>", partial(on_mouse_move))
    canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))

def draw_random_box(random_box, room_or_door_type, room_index):
        global canvas, reorganized_json, room_map

        x1, y1, x2, y2 = random_box
        room_type = int(room_or_door_type)
        room_color = room_id_to_color(room_type)
        box_id = draw_rectangle_and_label(canvas, x1, y1, x2, y2, room_color, room_index, room_type)
        reorganized_json["room_types"].insert(room_index, room_type)
        room_map[box_id] = random_box
    
        canvas.bind("<Button-1>", partial(on_mouse_down))
        canvas.bind("<B1-Motion>", partial(on_mouse_move))
        canvas.bind("<ButtonRelease-1>", partial(on_mouse_up))
        return room_index, room_or_door_type

def draw_line(canvas:Canvas, x1:float, y1:float, x2:float, y2:float, room_index:int, is_door:bool, room_type:int, door_type:int=None) -> int:
    """Input: canvas: canvas to draw on,
    x1,y1,x2,y2: coordinates of the line,
    room_index: index of the room or door that the line is associated with,
    is_door: boolean value if the line is associated with a door,
    room_type: type of the room or door that the line is associated with,
    door_type: type of the door that the line is associated with, if it does.
    Returns the item_id of the line drawn on the canvas.
    """
    line_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge",
                                                                                f"edge_room_index:{room_index}",
                                                                                f"edge_is_door:{is_door}",
                                                                                f"door_type:{door_type}",
                                                                                f"edge_room_type:{room_type}")) 
    return line_id

def draw_edges(data):
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
        for edge in edges:
            try:
                x1, y1, x2, y2, room_type, neighbor_room = edge
                door_type = room_type if is_door else None
                item_id = draw_line(canvas, x1, y1, x2, y2, room_index, is_door, room_type, door_type)
                edge_map[item_id] = edge                    
            except Exception as e:
                traceback.format_exc(e)

    canvas.bind("<Button-1>", partial(start_drag))
    canvas.bind("<B1-Motion>", partial(drag))
    canvas.bind("<ButtonRelease-1>", partial(end_drag))

def draw_random_edge(random_edges,box_index, rooms_or_doors, together_room_index, door_type=None):
    global canvas, reorganized_json, edge_map
    for edge in random_edges:
        x1, y1, x2, y2, room_type, neighbor_room = edge
        is_door = True if room_type > 11 else False
        item_id = draw_line(canvas, x1, y1, x2, y2, together_room_index, is_door, room_type, door_type)
        edge_map[item_id] = edge
        try:
            reorganized_json[rooms_or_doors][box_index]["edges"].append(edge)
        except Exception as e:
            traceback.format_exc(e)

def draw_random_door(direction):
    global ed_rm_list, room_type_sv

    try:
        door_type = room_name_to_id(room_type_sv.get())
        room_indexes = neigh_room_indexes_sv.get().split(",")
        room_types = neigh_room_types_sv.get().split(",")
    except Exception as e:
        traceback.format_exc(e)

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
    # but at the end, a new order is formed so in the beginning "doors" starts from key 1
    new_door_index = len(reorganized_json["rooms"])+len(reorganized_json["doors"])
    
    try:
        reorganized_json["doors"].update({new_door_index:{"boxes":random_door, "edges":[], "ed_rm":[], 
                                                      "room_type":room_type_sv.get()}})
    except KeyError as e:
        if str(e) == new_door_index:
            reorganized_json["doors"][new_door_index] = {"boxes":random_door,"edges":[],"ed_rm":[],
                                                     "room_type":room_type_sv.get()}



    if room_types[0] == '' or room_indexes[0] == '':
        messagebox.showerror("please fill entries", "no neighbors were added in entries")

    # update_edges_and_ed_rm_to_add_random_door(door_index, door_type, room_types, room_indexes)
    draw_random_box(random_door, door_type, new_door_index)


    # draw_random_edge(random_edges,new_door_index,"doors",door_type,new_together_door_index)
    draw_random_edge(random_edges=random_edges,
                     box_index=new_door_index,
                     rooms_or_doors="doors",
                     together_room_index=new_door_index,
                     door_type=door_type)

    if room_indexes == ['']:
        room_indexes = ['N','N','N','N']
    restoappend = append_ed_rm_list(new_door_index, room_indexes)
    for item in restoappend:
        try:
            reorganized_json["doors"][new_door_index]["ed_rm"].append(item)
        except KeyError as e:
            reorganized_json["doors"][new_door_index]["ed_rm"] = [item]

def draw_random_room():
    global ed_rm_list

    random_box = [400,90,450,130]

    room_index = get_last_room_index()
    room_type = room_name_to_id(room_type_sv.get())
    
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
    draw_random_box(random_box, room_type, room_index)

    if room_types == ['']:
        room_types = ['0','0','0','0']
    random_edges = [[400,90,400,130,room_type, int(room_types[0])],
                    [400,130,450,130,room_type, int(room_types[1])],
                    [450,130,450,90,room_type, int(room_types[2])],
                    [450,90,400,90,room_type, int(room_types[3])]]
    
    # room index twice is sent twice because of functionality related with draW_random_edge for doors
    draw_random_edge(random_edges=random_edges, 
                     box_index=room_index, 
                     rooms_or_doors="rooms", 
                     together_room_index=room_index, 
                     door_type=None)

    if room_indexes == ['']:
        room_indexes = ['N','N','N','N']
    restoappend = append_ed_rm_list(room_index, room_indexes)
    for item in restoappend:
        try:
            reorganized_json["rooms"][room_index]["ed_rm"].append(item)
        except KeyError as e:
            reorganized_json["rooms"][room_index]["ed_rm"] = [item]

def update_new_coords():
    global current_rectangle, action_type, room_map, canvas, room_index_together
    global room_edge_selection, reorganized_json

    if current_rectangle:
        new_coords = canvas.coords(current_rectangle)
        tags = canvas.gettags(current_rectangle)
        
        if current_rectangle in room_map:
            room_map[current_rectangle] = new_coords

            room_type = int(find_tag("room_type", tags))
            rooms_or_doors = "doors" if room_type > 11 else "rooms"
            room_index = int(find_tag("room_index", tags))
            reorganized_json[rooms_or_doors][room_index]["boxes"] = new_coords

        if room_edge_selection:
            update_edges_coords = canvas.find_withtag(f"edge_room_index:{room_index_together}")
            for i, edge in enumerate(update_edges_coords):
                new_coords = canvas.coords(edge)
                reorganized_json[rooms_or_doors][room_index_together]["edges"][i][:4] = new_coords

def on_close(path, message_label_middle):
    """input: original data format {"room_type"=[3,3,1,...], 
                                    "boxes"=[[58.0, 78.0, 130.0, 122.0],...], 
                                    "edges"=[[58.0, 122.0, 130.0, 122.0, 3, 1],...], # where 3 is current room_type and 1 is neighbor_room_type
                                    "ed_rm"=[[0], [0, 2],....]} # where 0 is corresponding room_index and 2 is neighbor_index
    """
    global reorganized_json
    # check all items on canvas 

    if len(reorganized_json["room_types"])!=0:
        if not edge_map:
            draw_edges(reorganized_json)
        if not room_map:
            draw_boxes(reorganized_json)

        """already updated reorganized_json with the new data in previous stages (end_drag, on_mouse_up)"""
        # newdata = concat_newdata_to_originaldata(originaldata)
        # reorganized_json = edit_json.reorganize_json(reorganized_json)
        original_format_json = edit_json.deorganize_format(reorganized_json)
        new_path = edit_json.dump_boxes(path, original_format_json)
        message_label_middle.config(text=new_path)
    else:
        original_format_json = {"room_type":[], "boxes":[], "edges":[], "ed_rm":[]}
        new_path = edit_json.dump_boxes(path, original_format_json)
        message_label_middle.config(text=new_path)


def on_clear(edit_json_frame, system_clear=False):
    global edge_map, room_map, reorganized_json, edge_selection, room_selection, ed_rm_list
    global start_x, start_y, current_edge, current_rectangle, drag_mode
    global canvas, combobox, room_edge_selection, room_index_together

    edge_map={}
    room_map = {}
    reorganized_json={"room_types":[], "rooms":{}, "doors":{}}
    ed_rm_list = []

    edge_selection = False
    room_selection = False
    room_edge_selection = False

    start_x = start_y = current_edge = current_rectangle = room_index_together = None
    drag_mode = None  # 'first', 'second', or None

    canvas =  tkinter.Canvas
    combobox = ttk.Combobox

    if not system_clear:
        init_gui(edit_json_frame, 800, 600, reorganized_json, "clear")

def get_last_room_index():
    if len(list(reorganized_json["rooms"])) == 0:
        room_index = 0
    else:
        room_index = list(reorganized_json["rooms"])[-1]+1
    return room_index

def change_tag_to_new_index(old_tag, new_tag):
    global canvas
    canvas.addtag_withtag(new_tag, old_tag)
    canvas.dtag(new_tag, old_tag)

def increment_doors_index(new_room_index, door_indexes):
    """is called only when adding new room because room is added 
    to the middle of the json and the doors indexes are all after the rooms."""
    combined_ed_list = []
    for value in {**reorganized_json["rooms"], **reorganized_json["doors"]}.values():
        for _list in value["ed_rm"]:
            combined_ed_list.append(_list)
        
    for ed_rm in combined_ed_list:
        if ed_rm[0] >= new_room_index:
            change_tag_to_new_index(f"room_index:{ed_rm[0]}", f"room_index:{ed_rm[0]+1}")
            change_tag_to_new_index(f"edge_room_index:{ed_rm[0]}", f"edge_room_index:{ed_rm[0]+1}")
            change_tag_to_new_index(f"label_box_index:{ed_rm[0]}", f"label_box_index:{ed_rm[0]+1}")
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
    This algorithm actually works if the neighbors are doors or rooms because only neighbors are being updated.
    so if a door neighbor is updated, then the door's neighbor will be a room V
    and if a room neighbor is updates, then the room's neighbor will be a room V
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

def append_ed_rm_list(room_index, neigh_room_indexes):
    res = []

    for i, neigh_index in enumerate(neigh_room_indexes):
        if neigh_index == 'N' or neigh_index == 'n':
            res.append([int(room_index)])
        else:
            res.append([room_index, int(neigh_index)])
    return res

def on_mouse_down(event):
    global current_rectangle, action_type, start_x, start_y, resize_edge, canvas
    global room_index_together, room_edge_selection, selected_index_sv, selected_type_sv

    item = canvas.find_closest(event.x, event.y)[0]
    tags = canvas.gettags(item)
    if "box" in tags:
        current_rectangle = item
        room_index = find_tag("room_index", tags)
        room_type = find_tag("room_type", tags)
        selected_index_sv.set(room_index)
        selected_type_sv.set(room_type+g.room_id_to_name(room_type))
        if room_edge_selection == True:
            room_index_together = int(room_index)
            canvas.itemconfigure("edge", width=0.5, fill="black")
            canvas.itemconfigure("box", width=2, outline="black")
            canvas.itemconfig(current_rectangle, outline="green")
            canvas.itemconfigure(f"edge_room_index:{room_index}", fill="green")

    elif "edge" in tags:
        try:
            if bool(find_tag("edge_is_door:",tags)):
                room_index = find_tag("edge_room_index", tags)
                room_index_together = int(room_index)
                room_type = find_tag("room_type", tags)
                current_rectangle = canvas.find_withtag(f"room_index:{room_index}")[0]
                canvas.itemconfigure("edge", width=0.5, fill="black")
                canvas.itemconfigure("box", width=2, outline="black")
                canvas.itemconfig(current_rectangle, outline="green")
                canvas.itemconfigure(f"edge_room_index:{room_index}", fill="green")
                selected_index_sv.set(value=room_index)
                selected_type_sv.set(value=room_type+g.room_id_to_name(room_type))
        except Exception as e:
            traceback.format_exc(e)

    elif "label" in tags:
        try:
            room_index = find_tag("label_box_index", tags)
            room_index_together = int(room_index)
            room_type = find_tag("label_box_type", tags)
            current_rectangle = canvas.find_withtag(f"room_index:{room_index}")[0]
            canvas.itemconfigure("edge", width=0.5, fill="black")
            canvas.itemconfigure("box", width=2, outline="black")
            canvas.itemconfig(current_rectangle, outline="green")
            canvas.itemconfigure(f"edge_room_index:{room_index}", fill="green")
            selected_index_sv.set(value=room_index)
            selected_type_sv.set(value=room_type+g.room_id_to_name(room_type))
        except Exception as e:
            traceback.format_exc(e)


    start_x, start_y = event.x, event.y
    try:
        x1, y1, x2, y2 = canvas.coords(current_rectangle)
    except:
        print(f"{g.RED}Error in on_mouse_down:current_rectangle: {current_rectangle}{g.RESET}")
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
        canvas.move(f"label_box_id:{current_rectangle}", dx, dy)
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

            room_type = int(find_tag("room_type", tags))
            rooms_or_doors = "doors" if room_type > 11 else "rooms"
            room_index = int(find_tag("room_index", tags))
            reorganized_json[rooms_or_doors][room_index]["boxes"] = new_coords

        if room_edge_selection:
            room_type = int(find_tag("room_type", tags))
            rooms_or_doors = "doors" if room_type > 11 else "rooms"
            update_edges_coords = canvas.find_withtag(f"edge_room_index:{room_index_together}")
            for i, edge in enumerate(update_edges_coords):
                new_coords = canvas.coords(edge)
                try:
                    reorganized_json[rooms_or_doors][room_index_together]["edges"][i][:4] = new_coords
                except Exception as ex:
                    print(f"{g.RED}Error in on_mouse_up: {ex}{g.RESET}")

        # current_rectangle = None

def start_drag(event):
    global start_x, start_y, current_edge, drag_mode, selected_edge, canvas
     
    item = canvas.find_closest(event.x, event.y)[0]  # Find the closest item to the click
    tags = canvas.gettags(item)
    if "edge" in tags:
        start_x, start_y = event.x, event.y
        current_edge = item
        for tag in tags:
            if tags[3].split(":")[1] == 'None':
                _type=tags[4].split(":")[1]
            else:
                _type=tags[3].split(":")[1]
            if "room_index" in tag:
                room_index = tag.split(":")[-1]
                selected_edge.set(room_index)                
                selected_index_sv.set(value=room_index)
                selected_type_sv.set(value=find_tag("room_index",tags)+" "+g.room_id_to_name(_type))
            if "edge_room_index" in tag:
                selected_index_sv.set(value=room_index)
                selected_type_sv.set(value=find_tag("edge_room_index",tags)+" "+g.room_id_to_name(_type))
            if "room_type" in tag:
                room_type = find_tag("room_type", tags)
                selected_type_sv.set(value=room_type)
                break

        canvas.itemconfig(current_edge, fill="green", width=2)
        line_coords = canvas.coords(current_edge)
        # Determine if the click is near an endpoint
        drag_mode = is_close_to_endpoint(start_x, start_y, line_coords)

def drag(event, _dx=None,_dy=None):
    global start_x, start_y, current_edge, drag_mode, current_rectangle
    global room_index_together, room_edge_selection, canvas

    if room_edge_selection:
        canvas.move(f"edge_room_index:{room_index_together}", _dx, _dy)

        if action_type == "resize":
            current_rectangle_coords = canvas.coords(current_rectangle)
            edges = canvas.find_withtag(f"edge_room_index:{room_index_together}")
            canvas.coords(edges[0], current_rectangle_coords[0], current_rectangle_coords[1], current_rectangle_coords[0], current_rectangle_coords[3])
            canvas.coords(edges[1], current_rectangle_coords[0], current_rectangle_coords[3], current_rectangle_coords[2], current_rectangle_coords[3])
            canvas.coords(edges[2], current_rectangle_coords[2], current_rectangle_coords[3], current_rectangle_coords[2], current_rectangle_coords[1])
            canvas.coords(edges[3], current_rectangle_coords[2], current_rectangle_coords[1], current_rectangle_coords[0], current_rectangle_coords[1])

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
            room_index = int(find_tag("room_index", tags))
            edge_index = int(find_tag("edge_index", tags))
            reorganized_json["rooms"][room_index]["edges"][edge_index][:4] = new_coords

        current_edge = None
        drag_mode = None

def on_mouse_down_together(event):
    on_mouse_down(event)

def on_mouse_move_together(event):
    dx,dy = on_mouse_move(event)
    drag(event,dx,dy)

def on_mouse_up_together(event):
    on_mouse_up(event)
    end_drag(event)
    
def move_up(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, 0, -units)  # Move up by 'units' units
    canvas.move(f"label_box_index:{room_index_together}", 0, -units)
    canvas.move(f"edge_room_index:{room_index_together}", 0, -units)
    update_new_coords()

def move_down(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, 0, units)  # Move down by 10 units
    canvas.move(f"label_box_index:{room_index_together}", 0, units)
    canvas.move(f"edge_room_index:{room_index_together}", 0, units)
    update_new_coords()

def move_left(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, -units, 0)  # Move left by 10 units
    canvas.move(f"label_box_index:{room_index_together}", -units, 0)
    canvas.move(f"edge_room_index:{room_index_together}", -units, 0)
    update_new_coords()

def move_right(event):
    global current_rectangle, canvas, room_index_together
    canvas.move(current_rectangle, units, 0)  # Move right by 10 units
    canvas.move(f"label_box_index:{room_index_together}", units, 0)
    canvas.move(f"edge_room_index:{room_index_together}",  units, 0)
    update_new_coords()

def move_edges_and_boxes_together():
    global room_edge_selection, canvas
    room_edge_selection = True
    canvas.bind("<Button-1>", partial(on_mouse_down_together))
    canvas.bind("<B1-Motion>", partial(on_mouse_move_together))
    canvas.bind("<ButtonRelease-1>", partial(on_mouse_up_together))
    canvas.bind("<Up>", partial(move_up))
    canvas.bind("<Down>", partial(move_down))
    canvas.bind("<Left>", partial(move_left))
    canvas.bind("<Right>", partial(move_right))

def create_new_tab(notebook_plots, name="Floor Plan"):
    from GUI.AppWidgets import MyFrame
    
    frame = MyFrame(notebook_plots)
    notebook_plots.tabs.append(frame)
    notebook_plots.add(frame, text=name)   
    notebook_plots.counter += 1 
    return frame

def handle_zip_file(zip_content):
    from io import BytesIO
    import zipfile

    zip_file_path = os.path.join(extraction_path, 'response.zip')
    with open(zip_file_path, 'wb') as file:
        file.write(zip_content)
    zip_in_memory = BytesIO(zip_content)
    with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
        zip_ref.extractall(extraction_path)

def save_canvas():
    global canvas
    from PIL import Image as PilImage

    canvas_ps_path = os.path.join(dump_path, "canvas.ps")
    canvas_img_path = os.path.join(dump_path, "canvas_image.png")

    canvas.postscript(file=canvas_ps_path, colormode='color')
    img = PilImage.open(canvas_ps_path)
    img.save(canvas_img_path, "png")

def generate_floorplan(self, path, message_label_middle,notebook_plots):
    global reorganized_json

    from requests import post
    from dotenv import load_dotenv
    from PIL import Image, ImageTk
    from datetime import datetime

    if len(reorganized_json["room_types"])!=0:
        if not edge_map:
            draw_edges(reorganized_json)
        if not room_map:
            draw_boxes(reorganized_json)

    original_format_json = edit_json.deorganize_format(reorganized_json)
    edit_json.dump_boxes(path, original_format_json)
    load_dotenv(env_path)
    url = os.getenv("URL")
    result = post(url, json=original_format_json)

    if result.status_code != 200:
        message_label_middle.config(text="Error on request to server. Please try again.")
        return
    
    handle_zip_file(result.content)
    save_canvas()
    
    timestamp = str(datetime.now().strftime("%H-%M-%S"))

    setattr(self, f"canvas_image_{timestamp}", Image.open(os.path.join(extraction_path,"app","dump", "canvas_image.png")))
    setattr(self, f"fp_image_{timestamp}", Image.open(os.path.join(extraction_path,"app","dump", "fp_0.png")))
    setattr(self, f"graph_image_{timestamp}", Image.open(os.path.join(extraction_path,"app","dump", "graph_0.png")))
    
    self.frame = create_new_tab(notebook_plots, name=f"{timestamp}")
    self.frame.grid_columnconfigure(0, weight=1)
    self.frame.grid_rowconfigure(0, weight=1)
    self.frame.grid_rowconfigure(1, weight=1)

    setattr(self, f"canvas_image_tk_{timestamp}", ImageTk.PhotoImage(getattr(self, f"canvas_image_{timestamp}")))
    setattr(self, f"fp_image_tk_{timestamp}", ImageTk.PhotoImage(getattr(self, f"fp_image_{timestamp}")))
    setattr(self, f"graph_image_tk_{timestamp}", ImageTk.PhotoImage(getattr(self, f"graph_image_{timestamp}")))

    setattr(self, f"canvas_image_tk_label_{timestamp}", ttk.Label(self.frame, image=getattr(self, f"canvas_image_tk_{timestamp}")))
    setattr(self, f"fp_image_tk_label_{timestamp}", ttk.Label(self.frame, image=getattr(self, f"fp_image_tk_{timestamp}")))
    setattr(self, f"graph_image_label_{timestamp}", ttk.Label(self.frame, image=getattr(self, f"graph_image_tk_{timestamp}")))

    getattr(self, f"canvas_image_tk_label_{timestamp}").grid(row=0, column=1, sticky="nswe")
    getattr(self, f"fp_image_tk_label_{timestamp}").grid(row=0, column=0, sticky="nswe")
    getattr(self, f"graph_image_label_{timestamp}").grid(row=1, column=0, sticky="nswe")
    
def print_all_tags():
    global canvas
    for item in canvas.find_all():
        print(canvas.gettags(item))
    

