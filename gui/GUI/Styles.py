from tkinter.ttk import Style

font_normal = ("Helvetica", 12)

class MyStyle:

    def __init__(self):
        super().__init__()
        self.my_style = Style()
        self.my_style.theme_use('clam')
        self.my_style.configure('GreenForeground.TLabel', foreground="green")
        self.my_style.configure('Custom.TCheckbutton', background="white", font=("Helvetica", 15))
        self.my_style.configure('Selected.TCheckbutton', background="yellow", font=("Helvetica", 15))
        self.my_style.configure('Custom.TFrame', background="white")
        self.my_style.configure('Blue.TButton', background="#73B8FA")
        self.my_style.configure('Green.TButton', background="green", activebackground="green")
        self.my_style.configure('Stop.TButton', background="red", foreground="redc")
        self.my_style.configure('Settings.TLabel', background='white')
        self.my_style.configure('Blue.TRadiobutton', indicatorforeground="#73B8FA")
        self.font_normal = ("Helvetica", 12)

        self.my_style.map('Blue.TRadiobutton',
                          indicatorforeground=[
                              ('!pressed', "#73B8FA"),
                              ('active', "#FFFF94")
                          ])

        self.my_style.map('Blue.TButton', background=[("active", "#FFFF94")])
        self.my_style.map('Stop.TButton', background=[("active", "green")])
