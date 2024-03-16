from tkinter import ttk
from tkinter.ttk import Button
import ParseNewJson.edit_json_gui as ejg

class CreateCanvasOptionsFrame(ttk.Frame):
    def __init__(self, parent,original_data,file_path_name,reorganized_json, main_frame, root):
        super().__init__(parent, style='Custom.TFrame')
        Button(self, text="Save new Json",
                command=lambda: ejg.on_close(original_data, file_path_name, main_frame.message_label_middle, root, reorganized_json))\
                    .grid(row=0, column=2, sticky="nw")
        Button(self, text="Clear", command=lambda: ejg.on_clear(main_frame))\
                    .grid(row=1, column=2, sticky="nw")
        Button(self, text="Room Selection", command=lambda: ejg.draw_boxes(reorganized_json, root))\
                    .grid(row=2,column=2, sticky='nw')
        Button(self, text="Edge selection", command=lambda: ejg.draw_edges(reorganized_json, root))\
                    .grid(row=3, column=2, sticky="nw")
        Button(self, text="Both Selection", command=lambda: ejg.move_edges_and_boxes_together())\
                    .grid(row=4, column=2, sticky='nw')