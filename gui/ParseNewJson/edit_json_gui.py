from functools import partial
import tkinter
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

edge_selection = False
room_selection = False
units = 1  # pixels

start_x = start_y = current_edge = current_rectangle = None
drag_mode = None  # 'first', 'second', or None

root=0

def move_up(event, canvas):
    global current_rectangle
    canvas.move(current_rectangle, 0, -units)  # Move up by 'units' units
    canvas.move(f"label-room-{current_rectangle}", 0, -units)

def move_down(event, canvas):
    global current_rectangle
    canvas.move(current_rectangle, 0, units)  # Move down by 10 units
    canvas.move(f"label-room-{current_rectangle}", 0, units)

def move_left(event, canvas):
    global current_rectangle
    canvas.move(current_rectangle, -units, 0)  # Move left by 10 units
    canvas.move(f"label-room-{current_rectangle}", -units, 0)

def move_right(event, canvas):
    global current_rectangle
    canvas.move(current_rectangle, units, 0)  # Move right by 10 units
    canvas.move(f"label-room-{current_rectangle}", units, 0)

def move_up(event, canvas):
    global current_rectangle
    canvas.move(current_rectangle, 0, -units)  # Move up by 10 units
    canvas.move(f"label-room-{current_rectangle}", 0, -units)

def on_canvas_click(event):
    print("Canvas clicked at", event.x, event.y)
    event.widget.focus_set()  # Set focus to the canvas when it's clicked

def draw_boxes(data, canvas, _root):
    global edge_selection, room_selection, root
    root = _root
    edge_selection = False
    room_selection = True

    if room_map != {}:
        canvas.itemconfigure("edge", width=0.5, fill="gray")
        canvas.itemconfigure("box", width=2, outline="black")
        canvas.tag_raise("box")
        canvas.tag_raise("label")
        return

    for room in data["rooms"].items():
        room_index = room[0]
        room_type = room[1]["room_type"]
        box = room[1]["boxes"]
        x1, y1, x2, y2 = box
        item_id = canvas.create_rectangle(x1, y1, x2, y2, fill="white", width=2, outline="black", tags=("box", f"{room_type}-{room_index}"))
        room_map[item_id] = box
        x, y = edit_json.calculate_averge_of_box(box)
        canvas.create_text(x, y, text=f"{room_index}", font=("Arial", 10), tags=(f"label-room-{item_id}", "label"))
    
    canvas.bind("<1>", on_canvas_click)
    canvas.bind("<Button-1>", partial(on_mouse_down, canvas=canvas))
    canvas.bind("<B1-Motion>", partial(on_mouse_move, canvas=canvas))
    canvas.bind("<ButtonRelease-1>", partial(on_mouse_up, canvas=canvas))
    root.bind("<Up>", partial(move_up, canvas=canvas))
    root.bind("<Down>", partial(move_down, canvas=canvas))
    root.bind("<Left>", partial(move_left, canvas=canvas))
    root.bind("<Right>", partial(move_right, canvas=canvas))

def on_mouse_down(event, canvas):
    global current_rectangle, action_type, start_x, start_y, resize_edge
    item = canvas.find_closest(event.x, event.y)[0]
    tags = canvas.gettags(item)
    if "box" in tags:
        current_rectangle = item
        print(f"Selected box: {current_rectangle}")
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

def on_mouse_move(event, canvas):
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

def on_mouse_up(event, canvas):
    global current_rectangle, action_type, room_map
    canvas.itemconfig(current_rectangle, outline="black")
    action_type = None

    if current_rectangle:
        new_coords = canvas.coords(current_rectangle)
        if current_rectangle in room_map:
            room_map[current_rectangle] = new_coords

        current_rectangle = None

def draw_edges(data, canvas, _root):
    global edge_selection, room_selection
    edge_selection = True
    room_selection = False
    
    if edge_map != {}:
        canvas.itemconfigure("edge", width=2, fill="black")
        canvas.itemconfigure("box", width=0.5, outline="gray")
        canvas.tag_raise("edge")
        canvas.tag_raise("label")

        return

    for room in data["rooms"].items():
        room_index = room[0]
        edges = room[1]["edges"]
        box = room[1]["boxes"]
        room_type = room[1]["room_type"]

        for edge in edges:
            try:
                x1, y1, x2, y2, room_type, neighbour_room = edge
                item_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge", f"{room_type}-{neighbour_room}"))
                edge_map[item_id] = edge

                if (room_type < 10):
                    x, y = edit_json.calculate_averge_of_box(box)
                    canvas.create_text(x, y, text=f"{room_index}", font=("Arial", 10), tags=(f"label-room-{room_index}", "label"))
            except Exception as e:
                traceback.format_exc(e)

    canvas.bind("<Button-1>", partial(start_drag, canvas=canvas))
    canvas.bind("<B1-Motion>", partial(drag, canvas=canvas))
    canvas.bind("<ButtonRelease-1>", partial(end_drag, canvas=canvas))

def start_drag(event, canvas):
    global start_x, start_y, current_edge, drag_mode
    item = canvas.find_closest(event.x, event.y)[0]  # Find the closest item to the click
    tags = canvas.gettags(item)
    if "edge" in tags:
        start_x, start_y = event.x, event.y
        current_edge = item
        canvas.itemconfig(current_edge, fill="green", width=2)
        line_coords = canvas.coords(current_edge)
        # Determine if the click is near an endpoint
        drag_mode = is_close_to_endpoint(start_x, start_y, line_coords)

def drag(event, canvas):
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

def end_drag(event, canvas):
    global current_edge, drag_mode
    if current_edge:
        canvas.itemconfig(current_edge, fill="black", width=2)
        new_coords = canvas.coords(current_edge)
        if current_edge in edge_map:
            edge_map[current_edge][:4] = new_coords

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

def output_newdata_to_original_format(data, canvas, _root):
    new_data = {
        "room_type": [],
        "boxes": [],
        "edges":[],
        "ed_rm":[]
    }

    new_data["room_type"] = data["room_type"]
    new_data["boxes"] = [value for value in room_map.values()]
    new_data["edges"] = [value for value in edge_map.values()]
    new_data["ed_rm"] = data["ed_rm"]

    return new_data

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

def on_close(data, path, message_label_middle, canvas, root, reor_data):
    # check all items on canvas 
    if not edge_map:
        draw_edges(reor_data, canvas, root)
    if not room_map:
        draw_boxes(reor_data, canvas, root)

    # create a json, in the format of the original json
    new_data = output_newdata_to_original_format(data, canvas, root)

    # reorganize the json for simplification
    reorganized_json = edit_json.reorganize_json(new_data)

    # fix edges that are outside of boxes
    # fixed_json = validate_data(reorganized_json)
    fixed_json = reorganized_json

    # convert new format to original format
    original_format_json = edit_json.from_new_format_to_original_format(fixed_json)

    new_path = dump_boxes(path, original_format_json)

    message_label_middle.config(text=new_path)


def on_clear(canvas) -> None:
    canvas.delete('all')