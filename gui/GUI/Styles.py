from tkinter.ttk import Style

font_normal = ("Helvetica", 12)

class MyStyle:

    def __init__(self):
        super().__init__()
        self.my_style = Style()
        self.my_style.theme_use('clam')
        self.my_style.configure('Custom.TFrame', background="white")
        self.my_style.configure('Blue.TButton', background="#73B8FA")
        self.my_style.configure('Pink.TButton', background=PinkPallete.get(3))
        self.my_style.configure('Green.TButton', background="green", activebackground="green")
        self.my_style.configure('Stop.TButton', background="red", foreground="redc")
        self.my_style.configure('Settings.TLabel', background='white')
        self.my_style.configure('Blue.TRadiobutton', indicatorforeground="#73B8FA")
        self.font_normal = ("Helvetica", 12)
        self.font_bold_big = ("Helvetica Bold", 24)
        self.font_bold_medium = ("Helvetica Bold", 16)
        self.my_style.configure('Hello.TLabel', background=PinkPallete.get(1), font=self.font_bold_big)
        self.my_style.configure('Welcome.TLabel', background=PinkPallete.get(1), font=self.font_bold_medium)

        self.my_style.map('Blue.TRadiobutton',
                          indicatorforeground=[
                              ('!pressed', "#73B8FA"),
                              ('active', "#FFFF94")
                          ])

        self.my_style.map('Blue.TButton', background=[("active", "#FFFF94")])
        self.my_style.map('Stop.TButton', background=[("active", "green")])

        self.my_style.map('Pink.TButton', background=[("active", PinkPallete.get(4))])

PinkPallete = {1:"#F9F5F6",
           2:"#F8E8EE",
           3:"#FDCEDF",
           4:"#F2BED1"}