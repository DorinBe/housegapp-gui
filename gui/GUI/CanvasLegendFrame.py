from tkinter import ttk
import tkinter as tk
from globals import ROOM_TYPES, ROOM_COLORS, room_id_to_name

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
