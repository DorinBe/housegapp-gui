import tkinter as tk

from frontend import main_gui

if __name__ == "__main__":
    window = tk.Tk()
    main_gui = main_gui.StartGUI(window)
    window.mainloop()
