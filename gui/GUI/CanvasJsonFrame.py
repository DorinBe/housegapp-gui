from tkinter import ttk
from tkinter.ttk import Button, Label, Entry, Combobox
import ParseNewJson.edit_json_gui as ejg


class CreateCanvasJsonFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='Custom.TFrame')

        Button(text="Add Room", master = self,command=lambda: ejg.add_random_room())\
            .grid(row=0, column=0, sticky='w')
        Button(text="Add Horizontal Door", master=self, command=lambda: ejg.add_random_door("horizontal"))\
            .grid(row=0, column=1, sticky='w')
        Button(text="Add Vertical Door", master=self, command=lambda: ejg.add_random_door("vertical"))\
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
        # Entry(master = self, width=10, textvariable=ejg.room_type_sv)\
        #     .grid(row=1, column=1, sticky='w')
        
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