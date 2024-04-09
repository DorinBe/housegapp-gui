from tkinter import ttk
from tkinter.ttk import Button
import ParseNewJson.edit_json_gui as ejg
from GUI.Utils import row_generate

class CreateCanvasOptionsFrame(ttk.Frame):
    def __init__(self, parent,file_path_name,reorganized_json, edit_json_frame, main_frame):
        super().__init__(parent, style='Custom.TFrame')
        row_i = row_generate()
        Button(self, text="Save new Json",
                command=lambda: ejg.on_close(file_path_name, edit_json_frame.message_label_middle))\
                    .grid(row=next(row_i), column=2, sticky="nw")
        Button(self, text="Clear", command=lambda: ejg.on_clear(edit_json_frame))\
                    .grid(row=next(row_i), column=2, sticky="nw")
        Button(self, text="Room Selection", command=lambda: ejg.draw_boxes(reorganized_json))\
                    .grid(row=next(row_i),column=2, sticky='nw')
        Button(self, text="Edge selection", command=lambda: ejg.draw_edges(reorganized_json))\
                    .grid(row=next(row_i), column=2, sticky="nw")
        Button(self, text="Both Selection", command=lambda: ejg.move_edges_and_boxes_together())\
                    .grid(row=next(row_i), column=2, sticky='nw')