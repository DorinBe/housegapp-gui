import tkinter as tk
from tkinter import ttk
import json
from functools import partial
import traceback

# ANSI escape codes
RED = '\033[31m'  # Red text
GREEN = '\033[32m'  # Green text
RESET = '\033[0m'  # Reset to default color
DEBUG = True

edge_map={}
rooms = {}

edge_selection = True
room_selection = False

def draw_edges(edges, canvas):
    global edge_map
    for edge in edges:
        x1, y1, x2, y2, room_index, neighbour_room = edge
        item_id = canvas.create_line(x1, y1, x2, y2, fill="black", width=2, tags=("edge", f"{room_index}-{neighbour_room}"))
        edge_map[item_id] = edge
    # Bind mouse events for edge editing
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
        new_coords = canvas.coords(current_edge)
        if current_edge in edge_map:
            edge_map[current_edge][:4] = new_coords

        current_edge = None
        drag_mode = None

def dump_boxes(filename):
    global rooms
    from datetime import datetime
    try:
        filename = filename + '_' + str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + '.json'
        with open(filename, 'a+') as file:
            json.dump(rooms, file)
    except Exception as e:
        return traceback.format_exc(e)
    return "File saved as " + filename

def recalculate_box(edges):
    global rooms
    x_coords = [coord for edge in edges for coord in (edge[0], edge[2])]
    y_coords = [coord for edge in edges for coord in (edge[1], edge[3])]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    return [x_min, y_min, x_max, y_max]

def recalculate_boxes(data):
    global rooms
    rooms["room_type"] = data["room_type"]
    rooms["edges"] = [value for value in edge_map.values()]
    rooms["ed_rm"] = data["ed_rm"]
    rooms["boxes"] = []
    prev=0
    edges = []
    for edge,index in zip(edge_map.values(), data["ed_rm"]):
        if prev == index[0]:
            edges.append(edge)
        else:
            rooms["boxes"].append(recalculate_box(edges))
            edges = [edge]
            prev = index[0]

def is_close_to_endpoint(x, y, line_coords, threshold=10):
    # Check if (x, y) is close to the line's endpoints
    x1, y1, x2, y2 = line_coords
    near_first_endpoint = (x - x1)**2 + (y - y1)**2 <= threshold**2
    near_second_endpoint = (x - x2)**2 + (y - y2)**2 <= threshold**2
    if near_first_endpoint:
        return 'first'
    elif near_second_endpoint:
        return 'second'
    return None

# Example: Saving when the GUI window is closed
def on_close(data, path, message_label_middle):
    recalculate_boxes(data)
    res = dump_boxes(path)
    message_label_middle.config(text=res)

start_x = start_y = current_edge = None
drag_mode = None  # 'first', 'second', or None
