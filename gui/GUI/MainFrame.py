import tkinter as tk
from tkinter import ttk as ttk
from GUI.Styles import PinkPallete as P
from PIL import Image, ImageTk
from Assets.Photos import photos


class CreateMainFrame(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # photos
        self.image_smting = Image.open(photos.house_logo)
        self.image_smting.thumbnail((200, 200))
        self.image_smting = ImageTk.PhotoImage(self.image_smting)

        self.background1_image  = Image.open(photos.bg1)
        self.background1_image  = ImageTk.PhotoImage(self.background1_image)

        self.background2_image  = Image.open(photos.bg2)
        self.background2_image  = ImageTk.PhotoImage(self.background2_image)

        # frames
        self.top_frame = tk.Frame(self.parent, bg=str(P.get(1)))
        self.left_frame = tk.Frame(self.parent, bg="#d8d8d8", pady=15)
        self.right_frame = tk.Frame(self.parent, bg="white")
        self.path_frame = tk.Frame(self.parent, bg=str(P.get(2)))
        self.message_frame = tk.Frame(self.parent, bg=str(P.get(2)))

        # buttons
        self.new_floorplan = ttk.Button(master=self.left_frame, text="New Floorplan", width=20, style='Pink.TButton')
        self.load_json_btn = ttk.Button(master=self.left_frame, text="Load JSON", width=20, style='Pink.TButton')
        self.stop_analyzing_btn = ttk.Button(master=self.left_frame,width=3, style='Stop.TButton')
        self.plots_radio = ttk.Radiobutton(self.left_frame, text='Rooms\t', width=10, style='Pink.TRadiobutton')
        self.download_btn = ttk.Button(self.left_frame, text='Download', width=10, style="Pink.TButton")
        self.settings_btn = ttk.Button(self.left_frame, text='Settings', width=10, style="Pink.TButton")
        self.signin_btn = ttk.Button(self.left_frame, text='Sign in', width=10, style="Pink.TButton")
        self.train_model_btn = ttk.Button(self.left_frame, text='Train Model', width=10, style="Pink.TButton")
        info_image = tk.PhotoImage(file=photos.info)
        self.info_btn = ttk.Button(self.left_frame, text='Info', width=10, style="Pink.TButton", image=info_image)
        
        self.path_label_left = tk.Label(self.path_frame, bg=str(P.get(2)), fg="black", text="", padx=10)
        self.path_label_middle = tk.Label(self.path_frame, bg=str(P.get(2)), fg="black", text="", font='Arial 15')
        self.path_label_right = tk.Label(self.path_frame, bg=str(P.get(2)), fg="black", text="")

        self.message_label_left = tk.Label(self.message_frame, bg=str(P.get(2)), fg="green", text="", padx=10)
        self.message_label_middle = tk.Label(self.message_frame, bg=str(P.get(2)), fg="green", text="",
                                             font='Arial 15 bold')
        self.message_label_right = tk.Label(self.message_frame, bg=str(P.get(2)), fg="green", text="")

        
        self.background1_label = tk.Label(self.top_frame, bg=str(P.get(1)), image=self.background1_image)
        self.bg_logo = tk.Label(self.top_frame, image=self.image_smting,bg=str(P.get(1)))
        self.background2_label = tk.Label(self.top_frame, bg=str(P.get(1)), image=self.background2_image)

        self.create_main_frame()

    def create_main_frame(self):
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(3, weight=10)

        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="nswe")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=1)
        self.top_frame.grid_rowconfigure(0, weight=1)

        #put background image in the top frame
        self.background1_label.grid(row=0, column=0)
        self.bg_logo.grid(row=0, column=1)
        self.background2_label.grid(row=0, column=2)

        self.left_frame.grid(row=3, rowspan=2, column=0, sticky="nsew")
        self.left_frame.columnconfigure(0, weight=1)

        # self.center_frame.grid(row=3, column=0, columnspan=3, sticky="nswe")

        self.right_frame.grid(row=3, column=1, columnspan=2, sticky="nswe")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.path_frame.grid(row=1, column=0, columnspan=3, sticky='ewn')
        self.path_frame.rowconfigure(0, weight=1)
        self.path_frame.columnconfigure(0, weight=1)
        self.path_frame.columnconfigure(1, weight=1)
        self.path_frame.columnconfigure(2, weight=1)

        self.message_frame.grid(row=2, column=0, columnspan=3, sticky='ewn')
        self.message_frame.rowconfigure(0, weight=1)
        self.message_frame.columnconfigure(0, weight=1)
        self.message_frame.columnconfigure(1, weight=1)
        self.message_frame.columnconfigure(2, weight=1)

        self.path_label_left.grid(row=0, column=0, sticky='ew')
        self.path_label_middle.grid(row=0, column=1, sticky="ew")
        self.path_label_right.grid(row=0, column=2, sticky='ew')

        self.message_label_left.grid(row=0, column=0, sticky='ew')
        self.message_label_middle.grid(row=0, column=1, sticky="ew")
        self.message_label_right.grid(row=0, column=2, sticky='ew')

        def row_generator(start:int):
            while True:
                yield start
                start+=1

        row_i = row_generator(0)
        self.new_floorplan.grid(row=next(row_i), column=0, padx=5, pady=5)
        self.load_json_btn.grid(row=next(row_i), column=0, padx=5, pady=5)
        self.download_btn.grid(row=next(row_i), column=0, padx=5, pady=5)
