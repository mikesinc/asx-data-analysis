import tkinter as tk
import tkinter.ttk as ttk

class tvwidget:
    def __init__(self, frame, relheight, relwidth, columns, firstColWidth=None, colWidth=None): #column as tuple
        #Construct Treeview
        self.treeview = ttk.Treeview(frame)
        self.treeview.place(relheight=relheight, relwidth=relwidth)
        self.treescrolly = ttk.Scrollbar(frame, orient="vertical", command=self.treeview.yview)
        self.treescrollx = ttk.Scrollbar(frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(xscrollcommand=self.treescrollx.set, yscrollcommand=self.treescrolly.set)
        self.treescrollx.pack(side="bottom", fill="x")
        self.treescrolly.pack(side="right", fill="y")
        #Define and format columns
        self.treeview["columns"] = columns
        self.treeview.column("#0", width=0, stretch=False)
        for column in self.treeview["columns"]:
            self.treeview.column(column, width=colWidth)
        self.treeview.column("Item", width=firstColWidth)
        #Create headings
        self.treeview.heading("#0", text="")
        for column in self.treeview["columns"]:
            self.treeview.heading(column, text=column, anchor="w")

    def insertValues(self, values, id):
        self.treeview.insert(parent="", index="end", iid=id, text="", values=values)