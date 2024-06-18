import tkinter as tk
from GUI import MainGui

if __name__ == "__main__":
    window = tk.Tk()
    main_gui = MainGui.StartGUI(window)
    window.mainloop()
