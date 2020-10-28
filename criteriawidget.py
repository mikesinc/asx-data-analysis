import tkinter as tk
import tkinter.ttk as ttk

class criteriawidget:
    def __init__(self, frame, criteria, startRow, startCol):
        tk.Label(frame, width=20, text=criteria, anchor="w").grid(row=startRow, column=startCol)
        tk.Label(frame, width=5, text="max", anchor="w").grid(row=startRow+1, column=startCol+1)
        tk.Label(frame, width=5, text="min", anchor="w").grid(row=startRow+2, column=startCol+1)
        self.maxCriteria = tk.Entry(frame, width=20)
        self.maxCriteria.grid(row=startRow+1, column=startCol)
        self.minCriteria = tk.Entry(frame, width=20)
        self.minCriteria.grid(row=startRow+2, column=startCol)

    def getBounds(self):
        return {
            "max": self.maxCriteria.get(),
            "min": self.minCriteria.get(),
            "screened": {}
        }
        