import tkinter as tk
import tkinter.ttk as ttk

class Calcinput:
    def __init__(self, frame, text, row, col):
        tk.Label(frame, width=20, text=text, anchor="w").grid(row=row, column=col)
        self.input = tk.Entry(frame, width=20)
        self.input.grid(row=row, column=col+1)

    def getEntry(self):
        return float(self.input.get())
