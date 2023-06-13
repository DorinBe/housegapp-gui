import tkinter as tk

from GUI import MainGui

if __name__ == "__main__":
    window = tk.Tk()  # create root window
    main_gui = MainGui.StartGUI(window)
    window.mainloop()
