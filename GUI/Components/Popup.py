import tkinter as tk
import tkinter.ttk as ttk
from Functions.sub_process import SubProcess
import os
import signal
import sys
from Components.Console import ConsoleFrame
import subprocess
import bcrypt
from . import config
import psutil

def kill_proc_tree(pid, including_parent=False):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)

class Popup:
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.title("Update Database")
        self.popup.geometry("800x250")
        self.popup.pack_propagate(False)
        self.popup.resizable(0, 0)    

        self.popup.protocol('WM_DELETE_WINDOW', self.on_closing)

        tk.Label(self.popup, text="This process will scrape the latest financial year data into the database and should hence only need to be done once a year.").pack()
        tk.Label(self.popup, text="This process may take up to 2 hours to complete. Recommended to not proceed unless necessary.").pack()

        tk.Label(self.popup, text="Morning Star Password: ").pack()
        self.pw = tk.Entry(self.popup, show="*")
        self.pw.pack()

        self.b1 = ttk.Button(self.popup, text='Proceed', width=30, command=self.update)
        self.b1.pack()
        self.b2 = ttk.Button(self.popup, text='Cancel', width=30, command=self.cancel)
        self.b2.pack()

        self.console = ConsoleFrame(self.popup)
        self.console.size().pack()
    
    def on_closing(self):
        proc = os.getpid()
        kill_proc_tree(proc)
        self.popup.destroy()

    def cancel(self):
        try:
            self.on_closing()
        except:
            self.popup.destroy()

    def update(self):
        # password check
        if not bcrypt.checkpw(self.pw.get().encode(), config.ms_password):
            self.console.get_textbox()['state'] = 'normal'
            self.console.get_textbox().delete("1.0", tk.END)
            self.console.get_textbox().insert("1.0", "Invalid Password, try again.")
            self.console.get_textbox()['state'] = 'disabled'
            return
        else:
            self.console.get_textbox()['state'] = 'normal'
            self.console.get_textbox().delete("1.0", tk.END)
            self.console.get_textbox()['state'] = 'disabled'

        self.proc = subprocess.Popen([
                sys.executable, os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\Functions', 'scrape.py')), 
                config.ms_username.encode(), 
                self.pw.get().encode(),
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # self.proc = subprocess.Popen([
        #         os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\Functions', 'scrape.exe')), 
        #         config.ms_username.encode(), 
        #         self.pw.get().encode()
        #     ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # self.proc = subprocess.Popen([
        #     os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\Functions', 'scrape.exe')), config.ms_username.encode(), self.pw.get().encode()
        # ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # self.proc = subprocess.Popen([
        #     os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\Functions', 'test.exe')), config.ms_username.encode(), self.pw.get().encode()
        # ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        SubProcess(
            self.popup,
            self.console.get_textbox(),
            self.proc
        )
