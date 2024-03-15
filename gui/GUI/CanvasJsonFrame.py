from tkinter import ttk
from tkinter.ttk import Button, Label, Entry
from ParseNewJson.edit_json_gui import add_random_room, add_random_door,\
    room_type_sv, neigh_room_indexes_sv, neigh_room_types_sv, neigh_door_indexes_sv, neigh_door_types_sv,selected_edge, selected_box, selected_door

class CreateCanvasJsonFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='Custom.TFrame')

        Button(text="Add Room", master = self,command=lambda: add_random_room())\
            .grid(row=0, column=0, sticky='w')
        Button(text="Add Door", master=self, command=lambda: add_random_door())\
            .grid(row=0, column=1, sticky='w')
        
        Label(text="Room Type:", master=self, )\
            .grid(row=1, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=room_type_sv)\
            .grid(row=1, column= 1, sticky='w')
        
        Label(text="Neigbor Room Indexes:", master=self, )\
            .grid(row=2, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=neigh_room_indexes_sv)\
            .grid(row=2, column= 1, sticky='w')
        
        Label(text="Neigbor Room Types:", master=self, )\
            .grid(row=3, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=neigh_room_types_sv)\
            .grid(row=3, column= 1, sticky='w')
        
        Label(text="Neigbor Door Indexes:", master=self, )\
            .grid(row=4, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=neigh_door_indexes_sv)\
            .grid(row=4, column= 1, sticky='w')
        
        Label(text="Neigbor Door Types:", master=self)\
            .grid(row=4, column=0, sticky="w")
        Entry(master = self, width=10, textvariable=neigh_door_types_sv)\
            .grid(row=4, column= 1, sticky='w')
        
        Label(text="Selected edge is in room: ", master=self)\
            .grid(row=5, column=0)
        Label(textvariable=selected_edge, master=self)\
            .grid(row=5, column=1, sticky='w')
        
        Label(text="Selected box: ", master=self)\
            .grid(row=6, column=0)
        Label(textvariable=selected_box, master=self)\
            .grid(row=6, column=1, sticky='w')