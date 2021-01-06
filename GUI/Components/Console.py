import tkinter as tk
import tkinter.ttk as ttk

#Frame for Input fields and buttons
class ConsoleFrame:
    def __init__(self, parent):
        #Define frame
        self.ConsoleFrame = ttk.LabelFrame(parent, text="Console Output")

        # show subprocess' stdout in GUI
        self.scrollbar = tk.Scrollbar(self.ConsoleFrame, orient='horizontal')
        self.scrollbar.pack(side='bottom', fill='x', expand='false')
        self.text = tk.Text(self.ConsoleFrame, wrap='none', xscrollcommand=self.scrollbar.set)
        self.text.pack(fill='x')
        self.scrollbar.config(command=self.text.xview)
    
    def size(self):
        return self.ConsoleFrame

    def get_textbox(self):
        return self.text
