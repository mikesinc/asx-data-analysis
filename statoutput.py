import tkinter as tk
import tkinter.ttk as ttk

class statoutput:
    def __init__(self, frame, text, row, col, width=None):
        tk.Label(frame, width=width, text=text, anchor="w").grid(row=row, column=col)
        self.cashYieldValue = tk.Label(frame, width=width, anchor="w")
        self.cashYieldValue.grid(row=row, column=col+1)
        self.evValue = tk.Label(frame, width=width, anchor="w")
        self.evValue.grid(row=row, column=col+2)
    
    def changeCashYield(self, text):
        self.cashYieldValue.config(text=text)

    def changeEvValue(self, text):
        self.evValue.config(text=text)

    def getCashYield(self):
        return float(self.cashYieldValue.cget("text"))

    def getEvValue(self):
        return float(self.evValue.cget("text"))
