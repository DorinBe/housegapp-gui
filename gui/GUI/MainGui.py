import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename

import pyautogui as pg
from GUI import AppWidgets
from GUI.AppWidgets import WhiteBGFrame, CreateEditCanvasFrame, CreateCanvasOptionsFrame, CreateCanvasLegendFrame, CreateMainFrame
from GUI.Styles import MyStyle

import json
from ParseNewJson import edit_json, edit_json_gui
from Assets.Photos import photos
from Assets.Jsons import jsons
from datetime import datetime
import os


MAX_X, MAX_Y = 1400, 800

# tabs globals
ad_new_tab_flag = False
admin_flag = False

class StartGUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.window = self.root = parent
        MyStyle()
        self.window.title(f"House-GAN++")  # title of the GUI window
        self.window.iconbitmap((photos.house_icon))  # icon of the GUI window
        place_center(self.window, width=MAX_X, height=MAX_Y)

        self.path = ""
        self.main_window = self.window
        self.num_of_rooms = 0

        self.main_frame = CreateMainFrame(self.main_window)
        self.configure_btns()

        # Notebooks
        self.notebook_plots = AppWidgets.ManagerScrollableNotebook(self.main_frame.right_frame)
        self.notebook_plots.grid(row=0, column=0, sticky="nswe")

        self.edit_json_frame = WhiteBGFrame

    def configure_btns(self):
        self.main_frame.load_json_btn.configure(command=lambda: self.open_file(extension='json'))
        self.main_frame.new_floorplan.configure(command=lambda: self.open_file("json", False))
        self.main_frame.download_btn.configure(command=self.download, state='disabled')


    def download(self):
        raise Exception("UnImplementedException")


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

    def select_all(self):
        for btn in self.btns:
            btn.state(['selected'])
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.ManagerScrollableNotebook(self.main_frame.right_frame)

    def deselect_all(self):
        for btn in self.btns:
            btn.state(['!selected'])
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.ManagerScrollableNotebook(self.main_frame.right_frame)

    def update_select_plots(self, site_name, btn_state):
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.ManagerScrollableNotebook(self.main_frame.right_frame)
   
def place_center(w1, width, height):  # Placing the window in the center of the screen
    reso = pg.size()
    rx = reso[0]
    ry = reso[1]
    x = int((rx / 2) - (width / 2))
    y = int((ry / 2) - (height / 2))
    width_str = str(width)
    height_str = str(height)
    w1.geometry(width_str + "x" + height_str + "+" + str(x) + "+" + str(y))

def show_hello_message(self):
    from GUI.Styles import PinkPallete as P
    self.main_frame.message_label_middle.config(text="Finished generating floor plan")
    text_frame = tk.Frame(self.main_frame.center_frame, bg=str(P.get(1)))
    button_frame = tk.Frame(self.main_frame.center_frame, bg=str(P.get(1)))

    text_frame.grid(row=0, sticky="nswe")
    button_frame.grid(row=1, sticky="nswe")
    text_frame.grid_columnconfigure(0, weight=1)
    text_frame.grid_rowconfigure(0, weight=1)
    text_frame.grid_rowconfigure(1, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_rowconfigure(0, weight=1)


    self.main_frame.center_frame.grid_columnconfigure(0, weight=1)

    hello_label = ttk.Label(text_frame, text="Hello =)", style="Hello.TLabel", anchor="n")
    welcome_label = ttk.Label(text_frame, text="Welcome to automatic floorplan generator!\n \tWould you like to do?", style="Welcome.TLabel", anchor="n")
    play_btn = ttk.Button(button_frame, text="Play with Bubble diagram", style="Pink.TButton", width=25, command=self.play_with_bubble_diagram_btn)
    upload_btn = ttk.Button(button_frame, text="Upload Bubble diagram", style="Pink.TButton", width=25, 
                            command=lambda: self.open_file(extension='*.*', dest_port=''))
    json_btn = ttk.Button(button_frame, text="Upload JSON", style="Pink.TButton", width=25,
                            command=lambda: self.open_file(extension='*.json', dest_port=''))
    login_btn = ttk.Button(button_frame, text="Login", style="Pink.TButton", command=self.signin_button, width=25)

    hello_label.grid(row=0, column=0, sticky="n",pady=(40,40))
    welcome_label.grid(row=1, column=0, sticky="n")

    play_btn.grid(row=0, column=0, sticky="n", padx=(400,0), pady=40)
    upload_btn.grid(row=0, column=1, sticky="n", pady=40)
    json_btn.grid(row=1, column=1, sticky="n", pady=40)
    login_btn.grid(row=0, column=2, sticky="n",padx=(0,200), pady=40)

    

