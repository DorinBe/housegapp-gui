from tkinter import ttk, Menu


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

class MyNotebook(ScrollableNotebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.counter = 0
        self.tabs = []


class MyFrame(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, style='Custom.TFrame')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(sticky='nswe')
