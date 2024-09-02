import os
from tkinter import ttk, StringVar, Canvas
from ParseNewJson import edit_json
from globals import room_id_to_color
from gui_path import env_path
from Assets.Extraction.extraction import extraction_path, dump_path
from PIL import Image, ImageTk
from datetime import datetime

class FloorPlanEditor:
    def __init__(self):
        self.room_map = {}
        self.edge_map = {}
        self.ed_rm_list = []
        self.reorganized_json = {}

        self.edge_selection = False
        self.current_edge = None

        self.room_selection = False
        self.current_rectangle = None

        self.room_edge_selection = False
        self.room_index_together = None

        self.start_x = None
        self.start_y = None
        self.drag_mode = None  # 'first', 'second', or None

        self.canvas = Canvas
        self.combobox = ttk.Combobox

        self.units = 1  # pixels

        self.room_type_sv = StringVar()
        self.neigh_room_indexes_sv = StringVar()
        self.neigh_room_types_sv = StringVar()
        self.neigh_door_indexes_sv = StringVar()
        self.neigh_door_types_sv = StringVar()
        self.selected_index_sv = StringVar()
        self.selected_type_sv = StringVar()

        self.MAX_X = 0
        self.MAX_Y = 0

    def init_gui(self, edit_json_frame, width, height, _reorganized_json, command: str):
        """Initialize GUI components."""
        self.on_clear(edit_json_frame, True)

        self.MAX_X = width - 500
        self.MAX_Y = height - 100
        self.reorganized_json = _reorganized_json

        self.canvas = Canvas(edit_json_frame, width=self.MAX_X, height=self.MAX_Y, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nswe")

        if command != "clear":
            self.room_type_sv = StringVar()
            self.neigh_door_indexes_sv = StringVar()
            self.neigh_room_types_sv = StringVar()
            self.neigh_room_indexes_sv = StringVar()
            self.neigh_door_types_sv = StringVar()
            self.selected_edge = StringVar()
            self.selected_index_sv = StringVar()
            self.selected_type_sv = StringVar()

            self.draw_boxes(self.reorganized_json)
            self.draw_edges(self.reorganized_json)

    def draw_rectangle_and_label(self, canvas: Canvas, x1: float, y1: float, x2: float, y2: float, outline_color: str, box_index: int, box_type: int, is_door: bool) -> int:
        """Draw rectangle and label on canvas."""
        box_id = canvas.create_rectangle(x1, y1, x2, y2, fill=outline_color, width=2, outline="black", tags=("box",
                                                                                                            f"room_index:{box_index}",
                                                                                                            f"room_type:{box_type}",
                                                                                                            f"is_door:{is_door}"))
        x, y = edit_json.calculate_average_of_box(box=(x1, y1, x2, y2))
        canvas.create_text(x, y, text=f"{box_index}", font=("Arial", 8), tags=("label",
                                                                                f"label_box_index:{box_index}",
                                                                                f"label_box_type:{box_type}",
                                                                                f"label_box_id:{box_id}",
                                                                                f"is_door:{is_door}"))
        return box_id

    def draw_boxes(self, data):
        """Draw boxes based on data."""
        self.edge_selection = False
        self.room_selection = True
        self.room_edge_selection = False
        self.room_index_together = None

        if self.room_map:  # rooms have been drawn
            self.canvas.itemconfigure("edge", width=0.5, fill="gray")
            self.canvas.itemconfigure("box", width=2, outline="black")
            self.canvas.tag_raise("box")
            self.canvas.tag_raise("label")
            self.canvas.tag_lower("edge")
        else:
            for room in {**data["rooms"], **data["doors"]}.items():
                room_index = room[0]
                room_type = room[1]["room_type"]
                is_door = room_type > 11
                room_color = room_id_to_color(room_type)

                box = room[1]["boxes"]
                x1, y1, x2, y2 = box
                item_id = self.draw_rectangle_and_label(self.canvas, x1, y1, x2, y2, room_color, room_index, room_type, is_door)
                self.room_map[item_id] = box

    # ... Include the other methods from your code here, refactored similarly ...

    def generate_floorplan(self, path, message_label_middle, notebook_plots):
        """Generate floor plan using a remote service."""
        from requests import post
        from dotenv import load_dotenv

        original_format_json, _ = self.preprocess_generation(path)
        load_dotenv(env_path)
        url = os.getenv("URL")
        result = post(url, json=original_format_json)

        if result.status_code != 200:
            message_label_middle.config(text="Error on request to server. Please try again.")
            return

        self.handle_zip_file(result.content)
        self.show_floorplan(path, message_label_middle, notebook_plots)

    def generate_floorplan_local_model(self, path, message_label_middle, notebook_plots):
        """Generate floor plan using a local model."""
        from houseganapp_min.local_main import generate

        original_format_json, saved_path = self.preprocess_generation(path)
        generate(saved_path)
        self.show_floorplan(path, message_label_middle, notebook_plots)

    # ... Continue refactoring other functions ...

    def preprocess_generation(self, path):
        """Preprocess data for floor plan generation."""
        if len(self.reorganized_json["room_types"]) != 0:
            if not self.edge_map:
                self.draw_edges(self.reorganized_json)
            if not self.room_map:
                self.draw_boxes(self.reorganized_json)

        original_format_json = edit_json.deorganize_format(self.reorganized_json)
        saved_path = edit_json.dump_boxes(path, original_format_json)
        return original_format_json, saved_path

    def show_floorplan(self, path, message_label_middle, notebook_plots):
        """Display the generated floor plan."""
        self.save_canvas()

        timestamp = str(datetime.now().strftime("%H-%M-%S"))

        setattr(self, f"canvas_image_{timestamp}", Image.open(os.path.join(extraction_path, "app", "dump", "canvas_image.png")))
        setattr(self, f"fp_image_{timestamp}", Image.open(os.path.join(extraction_path, "app", "dump", "fp_0.png")))
        setattr(self, f"graph_image_{timestamp}", Image.open(os.path.join(extraction_path, "app", "dump", "graph_0.png")))

        self.create_new_tab(notebook_plots, name=f"{timestamp}")

        setattr(self, f"canvas_image_tk_{timestamp}", ImageTk.PhotoImage(getattr(self, f"canvas_image_{timestamp}")))
        setattr(self, f"fp_image_tk_{timestamp}", ImageTk.PhotoImage(getattr(self, f"fp_image_{timestamp}")))
        setattr(self, f"graph_image_tk_{timestamp}", ImageTk.PhotoImage(getattr(self, f"graph_image_{timestamp}")))

        setattr(self, f"canvas_image_tk_label_{timestamp}", ttk.Label(notebook_plots.tabs[-1], image=getattr(self, f"canvas_image_tk_{timestamp}"), background="white", relief="solid", borderwidth=0.5))
        setattr(self, f"fp_image_tk_label_{timestamp}", ttk.Label(notebook_plots.tabs[-1], image=getattr(self, f"fp_image_tk_{timestamp}"), background="white", relief="solid", borderwidth=0.5))
        setattr(self, f"graph_image_label_{timestamp}", ttk.Label(notebook_plots.tabs[-1], image=getattr(self, f"graph_image_tk_{timestamp}"), background="white", relief="solid", borderwidth=0.5))

        getattr(self, f"canvas_image_tk_label_{timestamp}").grid(row=0, column=1, sticky="nswe")
        getattr(self, f"fp_image_tk_label_{timestamp}").grid(row=0, column=0, sticky="nswe")
        getattr(self, f"graph_image_label_{timestamp}").grid(row=1, column=0, sticky="nswe")

    def save_canvas(self):
        """Save the current canvas as an image."""
        canvas_ps_path = os.path.join(dump_path, "canvas.ps")
        canvas_img_path = os.path.join(dump_path, "canvas_image.png")

        self.canvas.post
