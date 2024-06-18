import tkinter as tk
from tkinter import ttk, Menu, DISABLED
from tkinter.ttk import Button, Label, Entry, Combobox

import ParseNewJson.edit_json_gui as ejg
from globals import ROOM_TYPES, ROOM_COLORS

from PIL import Image, ImageTk
from Assets.Photos import photos

from GUI.Utils import row_generate
from GUI.Styles import PinkPallete as P

# Copyright (c) Muhammet Emin TURGUT 2020
# For license see LICENSE
class ScrollableNotebook(ttk.Frame):
    def __init__(self, parent, wheelscroll=True, tabmenu=True, *args, **kwargs):
        super().__init__(master=parent)
        self.grid(sticky="nswe")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.xLocation = 0
        self.notebookContent = ttk.Notebook(self)
        self.notebookContent.grid(sticky="nswe")
        self.notebookTab = ttk.Notebook(self)
        self.notebookTab.bind("<<NotebookTabChanged>>", self._tabChanger)
        if wheelscroll:
            self.notebookTab.bind("<MouseWheel>", self._wheelscroll)
        slide_frame = ttk.Frame(self)
        self.menuSpace = 50
        if tabmenu:
            self.menuSpace = 50
            bottom_tab = ttk.Label(slide_frame, text="\u2630")
            bottom_tab.bind("<ButtonPress-1>", self._bottomMenu)

        left_arrow = ttk.Label(slide_frame, text=" \u276E")
        left_arrow.bind("<ButtonPress-1>", self._leftSlideStart)
        left_arrow.bind("<ButtonRelease-1>", self._slideStop)
        right_arrow = ttk.Label(slide_frame, text=" \u276F")
        right_arrow.bind("<ButtonPress-1>", self._rightSlideStart)
        right_arrow.bind("<ButtonRelease-1>", self._slideStop)
        self.notebookContent.bind("<Configure>", self._resetSlide)
        self.contentsManaged = []

        slide_frame.grid(row=0, column=1, sticky="nswe")
        bottom_tab.grid(row=0, column=1)
        left_arrow.grid(row=0, column=0)
        right_arrow.grid(row=0, column=2)

    def _wheelscroll(self, event):
        if event.delta > 0:
            self._leftSlide(event)
        else:
            self._rightSlide(event)

    def _bottomMenu(self, event):
        tab_list_menu = Menu(self, tearoff=0)
        for tab in self.notebookTab.tabs():
            tab_list_menu.add_command(label=self.notebookTab.tab(tab, option="text"),
                                      command=lambda temp=tab: self.select(temp))
        try:
            tab_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            tab_list_menu.grab_release()

    def _tabChanger(self, event):
        try:
            self.notebookContent.select(self.notebookTab.index("current"))
        except:
            print("problem")

    def _rightSlideStart(self, event=None):
        if self._rightSlide(event):
            self.timer = self.after(100, self._rightSlideStart)

    def _rightSlide(self, event):
        if self.notebookTab.winfo_width() > self.notebookContent.winfo_width() - self.menuSpace:
            if (self.notebookContent.winfo_width() - (
                    self.notebookTab.winfo_width() + self.notebookTab.winfo_x())) <= self.menuSpace + 5:
                self.xLocation -= 20
                self.notebookTab.place(x=self.xLocation, y=0)
                return True
        return False

    def _leftSlideStart(self, event=None):
        if self._leftSlide(event):
            self.timer = self.after(100, self._leftSlideStart)

    def _leftSlide(self, event):
        if not self.notebookTab.winfo_x() == 0:
            self.xLocation += 20
            self.notebookTab.place(x=self.xLocation, y=0)
            return True
        return False

    def _slideStop(self, event):
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None

    def _resetSlide(self, event=None):
        self.notebookTab.place(x=0, y=0)
        self.xLocation = 0

    def add(self, frame, **kwargs):
        if len(self.notebookTab.winfo_children()) != 0:
            self.notebookContent.add(frame, text="", state="hidden")
        else:
            self.notebookContent.add(frame, text="")
        self.notebookTab.add(ttk.Frame(self.notebookTab), **kwargs)
        self.contentsManaged.append(frame)

    def forget(self, tab_id):
        index = self.notebookTab.index(tab_id)
        self.notebookContent.forget(self.__ContentTabID(tab_id))
        self.notebookTab.forget(tab_id)
        self.contentsManaged[index].destroy()
        self.contentsManaged.pop(index)

    def hide(self, tab_id):
        self.notebookContent.hide(self.__ContentTabID(tab_id))
        self.notebookTab.hide(tab_id)

    def identify(self, x, y):
        return self.notebookTab.identify(x, y)

    def index(self, tab_id):
        return self.notebookTab.index(tab_id)

    def __ContentTabID(self, tab_id):
        return self.notebookContent.tabs()[self.notebookTab.tabs().index(tab_id)]

    def insert(self, pos, frame, **kwargs):
        self.notebookContent.insert(pos, frame, **kwargs)
        self.notebookTab.insert(pos, frame, **kwargs)

    def select(self, tab_id):
        # self.notebookContent.select(self.__ContentTabID(tab_id))
        self.notebookTab.select(tab_id)

    def tab(self, tab_id, option=None, **kwargs):
        kwargs_content = kwargs.copy()
        kwargs_content["text"] = ""  # important
        self.notebookContent.tab(self.__ContentTabID(tab_id), option=None, **kwargs_content)
        return self.notebookTab.tab(tab_id, option=None, **kwargs)

    def tabs(self):
        # return self.notebookContent.tabs()
        return self.notebookTab.tabs()

    def enable_traversal(self):
        self.notebookContent.enable_traversal()
        self.notebookTab.enable_traversal()

class ManagerScrollableNotebook(ScrollableNotebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.counter = 0
        self.tabs = []

class WhiteBGFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style='Custom.TFrame')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(sticky='nswe')

class CreateEditCanvasFrame(ttk.Frame):
    """Frame for editing canvas elements. It has buttons for adding room, door, etc."""

    def __init__(self, parent):
        super().__init__(parent, style='Custom.TFrame')

        Button(text="Add Room", master = self,command=lambda: ejg.draw_random_room())\
            .grid(row=0, column=0, sticky='w')
        Button(text="Add Horizontal Door", master=self, command=lambda: ejg.draw_random_door("horizontal"))\
            .grid(row=0, column=1, sticky='w')
        Button(text="Add Vertical Door", master=self, command=lambda: ejg.draw_random_door("vertical"))\
            .grid(row=0, column=2, sticky='w')
        
        Combobox(master=self, textvariable=ejg.room_type_sv, state= "readonly",
                  values = ["Living Room",
                            "Kitchen",
                            "Bedroom",
                            "Bathroom",
                            "Balcony",
                            "Entrance",
                            "Dining Room",
                            "Study Room",
                            "Storage",
                            "Front Door",
                            "Interior Door"])\
            .grid(row=1, column=1, sticky="w")
        
        Label(text="Room Type:", master=self, )\
            .grid(row=1, column=0, sticky="w")
        
        Label(text="Neighbor Room Indexes:", master=self, )\
            .grid(row=2, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=ejg.neigh_room_indexes_sv)\
            .grid(row=2, column= 1, sticky='w')
        
        Label(text="Neighbor Room Types:", master=self, )\
            .grid(row=3, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=ejg.neigh_room_types_sv)\
            .grid(row=3, column= 1, sticky='w')
        
        Label(text="Neighbor Door Indexes:", master=self, )\
            .grid(row=4, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=ejg.neigh_door_indexes_sv)\
            .grid(row=4, column= 1, sticky='w')
        
        Label(text="Neighbor Door Types:", master=self)\
            .grid(row=5, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=ejg.neigh_door_types_sv)\
            .grid(row=5, column= 1, sticky='w')
        
        Label(text="Selected index: ", master=self)\
            .grid(row=6, column=0)
        Label(textvariable=ejg.selected_index_sv, master=self)\
            .grid(row=6, column=1, sticky='w')
        
        Label(text="Selected type: ", master=self)\
            .grid(row=7, column=0)
        Label(textvariable=ejg.selected_type_sv, master=self)\
            .grid(row=7, column=1, sticky='w')
        
class CreateCanvasLegendFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='Custom.TFrame')

        for room_type in ROOM_TYPES:
            frame = tk.Frame(self, pady=2)
            frame.pack(side=tk.TOP, anchor=tk.W)

            _bg = ROOM_COLORS[ROOM_TYPES[room_type]]
            # Create the symbol as a small canvas square
            symbol = tk.Canvas(frame, width=20, height=20, bg=_bg , bd=0, highlightthickness=0)
            symbol.pack(side=tk.LEFT)

            # Create the label for the description
            label = tk.Label(frame, text=room_type)
            label.pack(side=tk.RIGHT)

class CreateCanvasOptionsFrame(ttk.Frame):
    def __init__(self, parent,file_path_name,reorganized_json, edit_json_frame, main_frame, notebook_plots:ManagerScrollableNotebook):
        super().__init__(parent, style='Custom.TFrame')
        row_i = row_generate()
        Button(self, text="Save new Json",
                command=lambda: ejg.on_close(file_path_name, main_frame.message_label_middle))\
                    .grid(row=next(row_i), column=2, sticky="nw")
        Button(self, text="Clear", command=lambda: ejg.on_clear(edit_json_frame))\
                    .grid(row=next(row_i), column=2, sticky="nw")
        Button(self, text="Room Selection", command=lambda: ejg.draw_boxes(reorganized_json))\
                    .grid(row=next(row_i),column=2, sticky='nw')
        Button(self, text="Edge selection", command=lambda: ejg.draw_edges(reorganized_json), state=DISABLED)\
                    .grid(row=next(row_i), column=2, sticky="nw")
        Button(self, text="Both Selection", command=lambda: ejg.move_edges_and_boxes_together())\
                    .grid(row=next(row_i), column=2, sticky='nw')
        Button(self,  text="Generate with GCP", command=lambda: \
               ejg.generate_floorplan(self, file_path_name, main_frame.message_label_middle,notebook_plots))\
                    .grid(row=next(row_i), column=2, sticky='nw')
        Button(self,  text="Generate with local .pth", command=lambda: \
            ejg.generate_floorplan_local_model(self, file_path_name, main_frame.message_label_middle,notebook_plots))\
                .grid(row=next(row_i), column=2, sticky='nw')
        
        Button(self,  text="Print tags", command=lambda: \
               ejg.print_all_tags())\
                    .grid(row=next(row_i), column=2, sticky='nw')
        
class CreateMainFrame(ttk.Frame):
    """Main frame of the application. It contains the buttons for creating new floorplan, loading json, etc."""

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
        self.plots_radio = ttk.Radiobutton(self.left_frame, text='Rooms\t', width=10, style='Pink.TRadiobutton')
        self.download_btn = ttk.Button(self.left_frame, text='Download', width=10, style="Pink.TButton")
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

        row_i = row_generate(0)
        self.new_floorplan.grid(row=next(row_i), column=0, padx=5, pady=5)
        self.load_json_btn.grid(row=next(row_i), column=0, padx=5, pady=5)
        self.download_btn.grid(row=next(row_i), column=0, padx=5, pady=5)
