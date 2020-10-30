import tkinter as tk
import tkinter.ttk as ttk

class Calcoutput:
    def __init__(self, frame, text, row, col, width=None):
        tk.Label(frame, width=width, text=text, anchor="w").grid(row=row, column=col)
        self.output = tk.Label(frame, width=width, anchor="w")
        self.output.grid(row=row, column=col+1)
    
    def changeText(self, text):
        self.output.config(text=text)

    def getValue(self):
        return float(self.output.cget("text"))
