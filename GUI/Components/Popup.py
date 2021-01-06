import tkinter as tk
import tkinter.ttk as ttk
from subprocess import Popen, PIPE
from Functions.sub_process import SubProcess
import os
import sys
from Components.Console import ConsoleFrame

class Popup:
    def __init__(self, root):
        self.popup = tk.Toplevel()
        self.popup.title("Update Database")
        self.popup.geometry("800x200")
        self.popup.pack_propagate(False)
        self.popup.resizable(0, 0)    
        self.root = root

        tk.Label(self.popup, text="This process will scrape the latest financial year data into the database and should hence only need to be done once a year.").pack()
        tk.Label(self.popup, text="This process may take up to 2 hours to complete. Recommended to not proceed unless necessary.").pack()

        self.b1 = ttk.Button(self.popup, text='Proceed with update', width=30, command=self.update)
        self.b1.pack()
        self.b2 = ttk.Button(self.popup, text='Cancel', width=10, command=self.popup.destroy)
        self.b2.pack()

        self.console = ConsoleFrame(self.popup)
        self.console.size().pack()

    def update(self):
        self.b1.destroy()
        self.b2.destroy()

        SubProcess(
            self.root,
            self.console.get_textbox(),
            Popen([
                sys.executable, os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\..\\database_scripts', 'test.py'))
            ],
                stdout=PIPE
            )
        )