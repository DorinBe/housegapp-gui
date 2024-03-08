import math
import time
import tkinter as tk
from threading import Thread
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Entry
from PIL import ImageTk
from PIL import Image

import matplotlib.backends.backend_tkagg as tkagg
import pyautogui as pg
from matplotlib import pyplot as plt

from GUI import AppWidgets, MainFrame
from GUI.AppWidgets import MyFrame
from GUI.Styles import MyStyle

import ctypes
import threading

import json
from ParseNewJson import edit_json, edit_json_gui

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
        self.window.iconbitmap("house_icon-removebg-preview.ico")
        place_center(self.window, width=MAX_X, height=MAX_Y)

        self.path = ""
        self.main_window = self.window
        self.selected = tk.IntVar()
        self.vars = []
        self.btns = [ttk.Checkbutton()]
        self.num_of_rooms = 0
        self.entries = None

        self.main_frame = MainFrame.CreateMainFrame(self.main_window)
        # self.ab = AppBoot.AppBoot(self.main_frame.message_label_middle)
        self.initial_program()

        # Notebooks
        self.notebook_plots = AppWidgets.MyNotebook(self.main_frame.right_frame)
        self.notebook_settings = AppWidgets.MyNotebook(self.main_frame.right_frame)

        # show_hello_message(self)

    def initial_program(self):
        # set functionalities to buttons
        self.main_frame.load_json_btn.configure(
            command=lambda: self.open_file(extension='json'))
        self.main_frame.plots_radio.configure(value=1, variable=self.selected, command=self.show_selected_size,
                                              state='disabled')
        self.main_frame.download_btn.configure(command=self.download, state='disabled')
        self.main_frame.signin_btn.configure(command=self.signin_button)

        self.selected.set(-1)

    def download(self):
        # get the image from the label
        image = self.floor_plan_label['image'][0]
        image.save('floor_plan.png')

    def open_file(self, extension):
        self.selected.set(-1)
        title = "Please choose " + extension + " file to work with"
        self.path = askopenfilename(filetypes=[("Custom Files:", extension)], title=title)
        self.main_frame.path_label_middle.configure(text="You selected "+self.path)
        if not self.path:
            print(f"Error opening file {self.path}")
            return
        file_path_name = self.path.split('.')[0]
        extension = self.path.split('.')[1]

        # clear graphs and notebooks data
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.MyNotebook(self.main_frame.right_frame)

        if extension == "json":
            with open(self.path) as file:
                original_data = json.load(file)

            # new
            reorganized_json = edit_json.reorganize_json(original_data)
            edit_json_gui.init_gui(self.main_frame, MAX_X, MAX_Y, original_data, reorganized_json, self.root, "init")

            # buttons
            self.save_new_json = ttk.Button(self.main_frame.right_frame, text="Save new Json", command=lambda: edit_json_gui.on_close(original_data, file_path_name, self.main_frame.message_label_middle, self.root, reorganized_json))
            self.edge_selection = ttk.Button(self.main_frame.right_frame, text="Edge selection", command=lambda: edit_json_gui.draw_edges(reorganized_json, self.root))
            self.room_selection = ttk.Button(self.main_frame.right_frame, text="Room selection", command=lambda: edit_json_gui.draw_boxes(reorganized_json, self.root))
            self.clear = ttk.Button(self.main_frame.right_frame, text="Clear", command=lambda: edit_json_gui.on_clear(self.main_frame))
            
            self.room_type_entry = ttk.Entry(self.main_frame.right_frame, width=10, text="Room Type", textvariable=edit_json_gui.room_type_sv)
            self.edges_neighbour_room_types = ttk.Entry(self.main_frame.right_frame, width=10, textvariable=edit_json_gui.edges_neighbour_room_types_sv)
            self.edges_neighbour_room_indexes = ttk.Entry(self.main_frame.right_frame, width=10, textvariable=edit_json_gui.edges_neighbour_room_indexes_sv)
            self.add_room_btn = ttk.Button(self.main_frame.right_frame, text="Add Room", 
                                            command=lambda: edit_json_gui.add_random_room())
            self.add_door_btn = ttk.Button(self.main_frame.right_frame, text="Add Door", 
                                                        command=lambda: edit_json_gui.add_random_door())
            

            
            # grid
            self.save_new_json.grid(row=0, column=1, sticky="w")
            self.clear.grid(row=1, column=1, sticky="w")
            self.save_new_json.grid(row=0, column=1, sticky="w")
            self.edge_selection.grid(row=2, column=1, sticky="w")
            self.room_selection.grid(row=3, column=1, sticky="w")
            self.add_room_btn.grid(row=4, column=1, sticky="w")
            self.add_door_btn.grid(row=5, column=1, sticky="w")
            ttk.Label(self.main_frame.right_frame, text="Room Type:").grid(row=6, column=1, sticky="w")
            self.room_type_entry.grid(row=6, column=2, sticky="w")
            ttk.Label(self.main_frame.right_frame, text="edges neighbour room types:").grid(row=7, column=1, sticky="w")
            self.edges_neighbour_room_types.grid(row=7, column=2, sticky="w")
            ttk.Label(self.main_frame.right_frame, text="edges neighbour room indexes:").grid(row=8, column=1, sticky="w")
            self.edges_neighbour_room_indexes.grid(row=8, column=2, sticky="w")

        # elif extensions of images
        elif extension == "png" or extension == "jpg" or extension == "jpeg":
            # create a new window
            self.new_window = tk.Toplevel(self.main_window, width=500, height=100)
            place_center(self.new_window, width=500, height=100)
            self.new_window.iconbitmap("house_icon-removebg-preview.ico")
            self.new_window.grid_columnconfigure(0, weight=1)
            self.new_window.grid_columnconfigure(1, weight=1)
            self.new_window.grid_columnconfigure(2, weight=1)
            self.new_window.grid_columnconfigure(3, weight=1)
            self.new_window.grid_rowconfigure(0, weight=1)
            self.new_window.grid_rowconfigure(1, weight=1)

            self.number_of_rooms = 4

            def choose_fixed():
                self.new_window.destroy()
                self.new_window = tk.Toplevel(self.main_window, width=500, height=100)
                place_center(self.new_window, width=500, height=100)
                self.new_window.iconbitmap("house_icon-removebg-preview.ico")
                self.new_window.grid_columnconfigure(0, weight=1)
                self.new_window.grid_rowconfigure(0, weight=1)
                ttk.Label(self.new_window, text="Fixed Heuristics refinement scheme is chosen.", style="Welcome.TLabel").grid(row=0, column=0)

            def choose_no_refinement():
                self.new_window.destroy()
                self.new_window = tk.Toplevel(self.main_window, width=500, height=100)
                place_center(self.new_window, width=500, height=100)
                self.new_window.iconbitmap("house_icon-removebg-preview.ico")
                self.new_window.grid_columnconfigure(0, weight=1)
                self.new_window.grid_rowconfigure(0, weight=1)
                ttk.Label(self.new_window, text="No refinement scheme is chosen.", style="Welcome.TLabel").grid(row=0, column=0)

            def choose_static_scheme():
                self.new_window.destroy()
                self.num_of_rooms =4 
                self.new_window = tk.Toplevel(self.main_window, width=500, height=400)
                place_center(self.new_window, width=500, height=200)
                self.new_window.iconbitmap("house_icon-removebg-preview.ico")
                for i in range(0, self.number_of_rooms+2):
                    self.new_window.grid_columnconfigure(i, weight=1)
                self.new_window.grid_rowconfigure(0, weight=1)
                self.new_window.grid_rowconfigure(1, weight=1)
                self.new_window.grid_rowconfigure(2, weight=1)
                self.new_window.grid_rowconfigure(3, weight=1)
                ttk.Label(self.new_window, text="Static refinement scheme is chosen.", style="Welcome.TLabel",anchor='center').grid(row=0, column=0, columnspan=self.number_of_rooms+2, sticky='w')

                for i in range(0,self.num_of_rooms,1):
                    ttk.Label(self.new_window, text="Room " + str(i+1), style="Welcome.TLabel").grid(row=1, column=i)
                    ttk.Entry(self.new_window, width=10).grid(row=2, column=i)
                ttk.Label(self.new_window, text="In doors",style="Welcome.TLabel").grid(row=1, column=self.num_of_rooms+1)
                ttk.Entry(self.new_window, width=10).grid(row=2, column=self.num_of_rooms+1)
                ttk.Label(self.new_window, text="Out doors", style="Welcome.TLabel").grid(row=1, column=self.num_of_rooms+2)
                ttk.Entry(self.new_window, width=10).grid(row=2, column=self.num_of_rooms+2)
                button = ttk.Button(self.new_window, text="Generate", style="Pink.TButton")
                button.grid(row=3, column=0, columnspan=self.number_of_rooms+2, sticky='nsew')

            def choose_dynamic_scheme():
                #copy static scheme
                self.new_window.destroy()
                self.num_of_rooms =4 
                self.new_window = tk.Toplevel(self.main_window, width=500, height=100)
                place_center(self.new_window, width=500, height=250)
                self.new_window.iconbitmap("house_icon-removebg-preview.ico")
                for i in range(0, self.number_of_rooms+2):
                    self.new_window.grid_columnconfigure(i, weight=1)
                self.new_window.grid_rowconfigure(0, weight=1)
                self.new_window.grid_rowconfigure(1, weight=1)
                self.new_window.grid_rowconfigure(2, weight=1)
                self.new_window.grid_rowconfigure(3, weight=1)
                ttk.Label(self.new_window, text="Static refinement scheme is chosen.", style="Welcome.TLabel",anchor='center').grid(row=0, column=0, columnspan=self.number_of_rooms+2, sticky='w')

                for i in range(0,self.num_of_rooms,1):
                    ttk.Label(self.new_window, text="Room " + str(i+1), style="Welcome.TLabel").grid(row=1, column=i)
                    ttk.Entry(self.new_window, width=10).grid(row=2, column=i)
                ttk.Label(self.new_window, text="In doors",style="Welcome.TLabel").grid(row=1, column=self.num_of_rooms+1)
                ttk.Entry(self.new_window, width=10).grid(row=2, column=self.num_of_rooms+1)
                ttk.Label(self.new_window, text="Out doors", style="Welcome.TLabel").grid(row=1, column=self.num_of_rooms+2)
                ttk.Entry(self.new_window, width=10).grid(row=2, column=self.num_of_rooms+2)

                self.new_window.grid_rowconfigure(4, weight=1)
                self.new_window.grid_rowconfigure(5, weight=1)
                for i in range(0,self.num_of_rooms,1):
                    ttk.Label(self.new_window, text="Room " + str(i+1), style="Welcome.TLabel").grid(row=3, column=i)
                    ttk.Entry(self.new_window, width=10).grid(row=4, column=i)
                ttk.Label(self.new_window, text="In doors",style="Welcome.TLabel").grid(row=3, column=self.num_of_rooms+1)
                ttk.Entry(self.new_window, width=10).grid(row=4, column=self.num_of_rooms+1)
                ttk.Label(self.new_window, text="Out doors", style="Welcome.TLabel").grid(row=3, column=self.num_of_rooms+2)
                ttk.Entry(self.new_window, width=10).grid(row=4, column=self.num_of_rooms+2)
                ttk.Button(self.new_window, text="Generate", style="Pink.TButton").grid(row=5, column=0,columnspan=self.number_of_rooms+2, sticky='ew')


            ttk.Label(self.new_window, text=f"System identified {self.number_of_rooms} rooms\nChoose desired refinement scheme", style="Welcome.TLabel").grid(row=0, column=0, columnspan=4)
            ttk.Button(self.new_window, text="No Refinement", style="Pink.TButton", command=choose_no_refinement).grid(row=1, column=0)
            ttk.Button(self.new_window, text="Fixed Heuristic", style="Pink.TButton", command=choose_fixed).grid(row=1, column=1)
            ttk.Button(self.new_window, text="Static Scheme", style="Pink.TButton",command=choose_static_scheme).grid(row=1, column=2)
            ttk.Button(self.new_window, text="Dynamic Scheme", style="Pink.TButton",command=choose_dynamic_scheme).grid(row=1, column=3)

            # # create a new frame
            # self.dynamic_scheme_frame = tk.Frame(self.new_window)
            # self.dynamic_scheme_frame.grid(row=0, column=0, sticky='nsew')
            # ttk.Label(self.dynamic_scheme_frame, text="HouseGan++ detected _ rooms").grid(row=0, columnspan=(self.num_of_rooms+4*2))
            # ttk.Label(self.dynamic_scheme_frame, text="Please initialize the refinement scheme mode if necessary").grid(row=1, columnspan=(self.num_of_rooms+4*2))

            # room_numer=1
            # out_i = 0
            # for i in range(0,self.num_of_rooms+4,2):
            #     ttk.Label(self.dynamic_scheme_frame, text="Room " + str(room_numer)).grid(row=2, column=i, sticky='w')
            #     ttk.Entry(self.dynamic_scheme_frame, width=10).grid(row=2, column=i+1, sticky='w')
            #     room_numer+=1
            #     out_i = i 
            # ttk.Label(self.dynamic_scheme_frame, text="In doors").grid(row=2, column=out_i, sticky='w')
            # ttk.Entry(self.dynamic_scheme_frame, width=10).grid(row=2, column=out_i+1, sticky='w')
            # ttk.Label(self.dynamic_scheme_frame, text="Out doors").grid(row=2, column=out_i+2, sticky='w')
            # ttk.Entry(self.dynamic_scheme_frame, width=10).grid(row=2, column=out_i+3, sticky='w')
            # room_numer=1
            # for i in range(0,self.num_of_rooms+4,2):
            #     ttk.Label(self.dynamic_scheme_frame, text="Room " + str(room_numer)).grid(row=3, column=i, sticky='w')
            #     ttk.Entry(self.dynamic_scheme_frame, width=10).grid(row=3, column=i+1, sticky='w')
            #     room_numer+=1
            #     out_i = i 
            # ttk.Label(self.dynamic_scheme_frame, text="In doors").grid(row=3, column=out_i, sticky='w')
            # ttk.Entry(self.dynamic_scheme_frame, width=10).grid(row=3, column=out_i+1, sticky='w')
            # ttk.Label(self.dynamic_scheme_frame, text="Out doors").grid(row=3, column=out_i+2, sticky='w')
            # ttk.Entry(self.dynamic_scheme_frame, width=10).grid(row=3, column=out_i+3, sticky='w')
            # ttk.Button(self.dynamic_scheme_frame, text="OK", command=self.new_window.destroy, style="Blue.TButton").grid(row=3, columnspan=(self.num_of_rooms+4*2))

        else:
            messagebox.showerror(message="Selected file is not supported.")
            return

    def show_selected_size(self):
        if self.selected.get() == 1:
            self.select_plots()

    def select_plots(self):
        global ad_new_tab_flag

        self.selected.set(1)
        self.notebook_settings.grid_remove()

        frame = MyFrame(self.notebook_plots)
        self.notebook_plots.tabs.append(frame)
        self.notebook_plots.add(frame, text="Floor Plan")    

        # pick_sites_label = ttk.Label(frame, style="Settings.TLabel", text=pick_sites_text, font=("Helvetica", 12))
        # show 'floorplan.png' in the frame
        self.img = ImageTk.PhotoImage(Image.open("floorplan.png"))
        self.floor_plan_label = ttk.Label(frame, image=self.img)
        self.floor_plan_label.grid(row=0, column=0)
        # floor_plan_label.grid_columnconfigure(0, weight=1)
        # floor_plan_label.grid_rowconfigure(0, weight=1)
        # self.notebook_plots.counter += 1

        self.main_frame.plots_radio['state'] = 'normal'
        self.main_frame.download_btn['state'] = 'normal'
        self.main_frame.settings_btn['state'] = 'normal'
        self.notebook_plots.grid(row=0, column=0, sticky="nswe")
        ad_new_tab_flag = False

    def signin_button(self):
        self.selected.set(-1)
        # self.main_frame.center_frame.grid_remove()

        # create pop up window of sign in
        self.signin_window = tk.Toplevel(self.main_window)
        self.signin_window.title("Sign in")
        # self.signin_window.geometry("350x200")
        self.signin_window.resizable(False, False)

        # create a frame for the sign in window
        self.signin_frame = ttk.Frame(self.signin_window, style='Custom.TFrame')
        self.signin_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")  # Add some padding
        self.signin_frame.grid_columnconfigure(0, weight=1)  # Make the frame stretch when resizing
        self.signin_frame.grid_rowconfigure(0, weight=1)  # Make the frame stretch when resizing
        self.signin_frame.grid_propagate(True)  # Disable resizing the frame

        # create a label for the sign in window
        self.signin_label = ttk.Label(self.signin_frame, style="Settings.TLabel", text="Sign in", font=("Helvetica", 16))
        self.signin_label.grid(row=0, column=0, columnspan=2, padx=(20,20), pady=(20,20))  # Let it span 2 columns and align to left

        # create a label for the username
        self.username_label = ttk.Label(self.signin_frame, style="Settings.TLabel", text="Username", font=("Helvetica", 12))
        self.username_label.grid(row=1, column=0, sticky="w", padx=(20,20), pady=(0,0))  # Align to left

        # create a label for the password
        self.password_label = ttk.Label(self.signin_frame, style="Settings.TLabel", text="Password", font=("Helvetica", 12))
        self.password_label.grid(row=2, column=0, sticky="w", padx=(20,20), pady=(0,20))  # Align to left

        # create a entry for the username
        self.username_entry = ttk.Entry(self.signin_frame, style="Settings.TEntry", font=("Helvetica", 12))
        self.username_entry.grid(row=1, column=1, sticky="e", padx=(0,20), pady=(0,0))  # Align to right

        # create a entry for the password
        self.password_entry = ttk.Entry(self.signin_frame, style="Settings.TEntry", font=("Helvetica", 12))
        self.password_entry.grid(row=2, column=1, sticky="e", padx=(0,20), pady=(0,20))  # Align to right

        # create a button for the sign in
        self.login_btn = ttk.Button(self.signin_frame, style="Pink.TButton", text="Login", command=self.login)
        self.login_btn.grid(row=3, column=0, columnspan=2, padx=(20,20), pady=(0,20))  # Let it span 2 columns and align to right
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            self.signin_window.destroy()
            self.main_frame.settings_btn['state'] = 'normal'
            self.main_frame.download_btn['state'] = 'normal'
            self.main_frame.plots_radio['state'] = 'normal'
            self.main_frame.signin_btn['style'] = 'Green.TButton'
            self.add_train_model_button()
        else:
            messagebox.showerror("Error", "Wrong username or password")

    def add_train_model_button(self):
        self.main_frame.train_model_btn.grid(row=6, column=0, padx=5, pady=5)

    def select_all(self):
        for btn in self.btns:
            btn.state(['selected'])
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.MyNotebook(self.main_frame.right_frame)

    def deselect_all(self):
        for btn in self.btns:
            btn.state(['!selected'])
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.MyNotebook(self.main_frame.right_frame)

    def update_select_plots(self, site_name, btn_state):
        self.notebook_plots = self.notebook_plots.destroy()
        self.notebook_plots = AppWidgets.MyNotebook(self.main_frame.right_frame)
   
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
    # train_btn.grid(row=0, column=3, sticky="n", pady=40, padx=(0,100))

    

