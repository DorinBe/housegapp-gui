import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename

import pyautogui as pg
from GUI import Frames
from GUI.Frames import WhiteBGFrame, CreateEditCanvasFrame, CreateCanvasOptionsFrame, CreateCanvasLegendFrame, CreateMainFrame
from GUI.Styles import MyStyle

import json
from ParseNewJson import edit_json, edit_json_gui
from Assets.Photos import photos
from Assets.Jsons import jsons
from datetime import datetime
import os

MAX_X, MAX_Y = 1400, 800

class StartGUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.window = parent
        MyStyle()
        self.window.title(f"House-GAN++")
        self.window.iconbitmap((photos.house_icon))
        place_center(self.window, width=MAX_X, height=MAX_Y)

        self.path = ""

        self.main_frame = CreateMainFrame(self.window)
        self.configure_buttons()

        # Notebooks
        self.notebook_plots = Frames.ManagerScrollableNotebook(self.main_frame.right_frame)
        self.notebook_plots.grid(row=0, column=0, sticky="nswe")

        self.edit_json_frame = WhiteBGFrame

    def configure_buttons(self):
        self.main_frame.load_json_btn.configure(command=lambda: self.open_file(extension='json'))
        self.main_frame.new_floorplan.configure(command=lambda: self.open_file("json", False))


    def open_file(self, extension, really_open=True):
        if really_open:
            title = "Please choose " + extension + " file to work with"
            self.path = askopenfilename(filetypes=[("Custom Files:", extension)], title=title)            
            if not self.path:
                print(f"Error opening file {self.path}")
                return
        else:
            self.path = os.path.join(jsons.jsons_dir, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.json')
            with open(self.path, 'w') as file: # force new json file with empty data
                file.write('{"room_type": [], "boxes": [], "edges": [], "ed_rm": []}')
            self.path = self.path.replace(f'\\', '/')

        self.ano_path = ""
        for p in self.path.split('/')[3:]:
            self.ano_path = os.path.join(self.ano_path, p)

        self.main_frame.path_label_middle.configure(text="Opened "+self.ano_path)
        file_path_name = os.path.basename(self.path)
        extension = os.path.splitext(self.path)[1]

        if not isinstance(self.edit_json_frame, WhiteBGFrame):
            self.edit_json_frame = WhiteBGFrame(self.notebook_plots)
            self.notebook_plots.tabs.append(self.edit_json_frame)
            self.notebook_plots.add(self.edit_json_frame, text="Edit JSON") 
            self.notebook_plots.counter += 1

        if extension == ".json":
            with open(self.path) as file:
                original_data = json.load(file)
            reorganized_json = edit_json.reorganize_json(original_data)
            edit_json_gui.init_gui(self.edit_json_frame, MAX_X, MAX_Y, reorganized_json, "init")
            CreateCanvasOptionsFrame(\
                parent=self.edit_json_frame, file_path_name=self.path, reorganized_json=reorganized_json,\
                edit_json_frame=self.edit_json_frame, main_frame=self.main_frame, notebook_plots=self.notebook_plots)\
                .grid(row=0, column=3, sticky='nw')
            CreateEditCanvasFrame(self.edit_json_frame)\
                .grid(row=1, column=0, sticky='nw')
            CreateCanvasLegendFrame(self.edit_json_frame)\
                .grid(row=0, column=2, sticky='nw')
        else:
            messagebox.showerror(message="Selected file is not supported.")
            return
   
def place_center(w1, width, height):
    """Place window at center of screen"""
    resolution = pg.size()
    rx = resolution[0]
    ry = resolution[1]
    x = int((rx / 2) - (width / 2))
    y = int((ry / 2) - (height / 2))
    width_str = str(width)
    height_str = str(height)
    w1.geometry(width_str + "x" + height_str + "+" + str(x) + "+" + str(y))