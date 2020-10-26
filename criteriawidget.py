import tkinter as tk
import tkinter.ttk as ttk

class criteriawidget:
    def __init__(self, frame, criteria, startRow, startCol):
        tk.Label(frame, width=20, text=criteria, anchor="w").grid(row=startRow, column=startCol)
        tk.Label(frame, width=5, text="max", anchor="w").grid(row=startRow+1, column=startCol+1)
        tk.Label(frame, width=5, text="min", anchor="w").grid(row=startRow+2, column=startCol+1)
        tk.Entry(frame, width=20).grid(row=startRow+1, column=startCol)
        tk.Entry(frame, width=20).grid(row=startRow+2, column=startCol)
        