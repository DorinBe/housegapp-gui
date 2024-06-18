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
JSON_EXTENSION = "json"

def configure_buttons(main_frame, file_handler):
    main_frame.load_json_btn.configure(command=lambda: file_handler.open_file(extension='json'))
    main_frame.new_floorplan.configure(command=lambda: file_handler.open_file("json", False))

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

class FileHandler():
    """Handles file opening and processing and updates the GUI accordingly."""

    def __init__(self, main_frame, notebook_plots):
        self.main_frame = main_frame
        self.notebook_plots = notebook_plots
        self.path = ""
        self.edit_json_frame = None

    def open_file(self, extension, is_new_floor_plan=True):
        """Open or create a file based on the selected button."""
        if is_new_floor_plan:
            self.path = self.select_existing_json_file(extension)
            if not self.path:
                self.show_error(f"Error opening file {self.path}")
                return
        else:
            self.path = self.create_initialized_json_file()

        self.update_path_label()
        self.process_file(extension)

    def select_existing_json_file(self, extension):
        """Open file selection dialog, returns the path of the selected json file."""
        title = "Please choose " + extension + " file to work with"
        return askopenfilename(filetypes=[("Custom Files:", extension)], title=title)
    
    def create_initialized_json_file(self):
        """Creates a new json file with structure of input to HouseGAN++ model."""
        path = os.path.join(jsons.jsons_dir, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.json')
        with open(path, 'w') as file:
            file.write('{"room_type": [], "boxes": [], "edges": [], "ed_rm": []}')
        return path.replace(f'\\', '/')
    
    def show_error(self, message):
        messagebox.showerror(message=message)

    def update_path_label(self):
        ano_path = os.path.join(*self.path.split('/')[3:])
        self.main_frame.path_label_middle.configure(text="Opened " + ano_path)

    def process_file(self, extension):
        """Processes the opened json file and initialized the GUI components"""
        if not isinstance(self.edit_json_frame, WhiteBGFrame):
            self.edit_json_frame = WhiteBGFrame(self.notebook_plots)
            self.notebook_plots.tabs.append(self.edit_json_frame)
            self.notebook_plots.add(self.edit_json_frame, text="Edit JSON")
            self.notebook_plots.counter += 1

        if extension == JSON_EXTENSION:
            with open(self.path) as file:
                original_data = json.load(file)
            reorganized_json = edit_json.reorganize_json(original_data)
            self.initialize_edit_json_gui(reorganized_json)
        else:
            self.show_error("Selected file is not supported.")
            return

    def initialize_edit_json_gui(self, reorganized_json):
        """Initializes the GUI components for editing the json file."""
        edit_json_gui.init_gui(self.edit_json_frame, MAX_X, MAX_Y, reorganized_json, "init")
        CreateCanvasOptionsFrame(
            parent=self.edit_json_frame,
            file_path_name=self.path,
            reorganized_json=reorganized_json,
            edit_json_frame=self.edit_json_frame,
            main_frame=self.main_frame,
            notebook_plots=self.notebook_plots
        ).grid(row=0, column=3, sticky='nw')
        CreateEditCanvasFrame(self.edit_json_frame).grid(row=1, column=0, sticky='nw')
        CreateCanvasLegendFrame(self.edit_json_frame).grid(row=0, column=2, sticky='nw')

class StartGUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.window = parent
        MyStyle()
        self.window.title(f"House-GAN++")
        self.window.iconbitmap((photos.house_icon))
        place_center(self.window, width=MAX_X, height=MAX_Y)

        self.main_frame = self.create_main_frame()
        self.notebook_plots = Frames.ManagerScrollableNotebook(self.main_frame.right_frame)
        self.notebook_plots.grid(row=0, column=0, sticky="nswe")

        self.file_handler = FileHandler(self.main_frame, self.notebook_plots)
        configure_buttons(self.main_frame, self.file_handler)

    def create_main_frame(self):
        return CreateMainFrame(self.window)