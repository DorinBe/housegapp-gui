def draw_boxes(data, canvas):
    # delete all items on canvas
    canvas.delete("edge")
    canvas.delete("box")
    for box in data["boxes"]:
        x1, y1, x2, y2 = box
        canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2, tags="box")