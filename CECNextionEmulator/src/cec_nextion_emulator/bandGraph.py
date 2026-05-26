#!/usr/bin/python3
"""
bandGraph

reuseable band graph object

UI source file: bandGraph.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import bandGraphui as baseui


#
# Manual user code
#

class bandGraph(baseui.bandGraphUI):
    def __init__(self, master=None,  **kw):

        super().__init__(master, **kw)
        # print("allocating a band")
        # self.bandScannerWindow = bandScannerWindow
    #
    #   This function allows the attachment of a callback within the GraphPak object
    #   for scrollbar movement after the bandGraph has been created. This callback
    #   handles movement of the scrollbar and calculation of the beginning and ending of the scan region
    #
    #   Each bandGraph object is attached to a single GraphObject.

    def attachScrollbar_CB (self, scrollbar_callback): #, currentFrequency_callback):
        self.scrollbar_CB = scrollbar_callback
        # self.currentFrequency_CB = currentFrequency_callback

    def bandStart_CB(self, scale_value):
        self.scrollbar_CB(scale_value )
        # self.currentFrequency_CB()





if __name__ == "__main__":
    root = tk.Tk()
    widget = bandGraph(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
