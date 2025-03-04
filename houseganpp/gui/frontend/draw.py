from tkinter import Canvas
from backend.edit_json import calculate_average_of_box
"""draws elements on ui"""

def draw_rectangle_and_label(canvas:Canvas, x1:float, y1:float, x2:float, y2:float, outline_color:str, box_index:int, box_type:int, is_door:bool) -> int:
    """Input: canvas: canvas to draw on, 
    x1,y1,x2,y2: coordinates of the box,
    outline_color: outline colors of the box,
    box_index: index of the room or door,
    box_type: type of the box room or door (Living Room, Front Door, etc.)
    Returns the item_id of the rectangle drawn on the canvas."""
    box_id = canvas.create_rectangle(x1, y1, x2, y2, fill=outline_color, width=2, outline="black", tags=("box",
                                                                                                        f"room_index:{box_index}",
                                                                                                        f"room_type:{box_type}",
                                                                                                        f"is_door:{is_door}"))
    x, y = calculate_average_of_box(box=(x1, y1, x2, y2))
    canvas.create_text(x, y, text=f"{box_index}", font=("Arial", 8), tags=("label",
                                                                            f"label_box_index:{box_index}",
                                                                            f"label_box_type:{box_type}",
                                                                            f"label_box_id:{box_id}",
                                                                            f"is_door:{is_door}"))
    return box_id

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
                                                                                f"is_door:{is_door}",
                                                                                f"door_type:{door_type}",
                                                                                f"edge_room_type:{room_type}")) 
    return line_id