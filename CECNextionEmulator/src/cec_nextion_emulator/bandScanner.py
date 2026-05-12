#!/usr/bin/python3
"""
Band Scanner

Scans up to three selected bands for signals.

UI source file: bandScanner.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import bandScannerui as baseui


#
# Manual user code
#

class bandScanner(baseui.bandScannerUI):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)


if __name__ == "__main__":
    root = tk.Tk()
    widget = bandScanner(root)
    root.mainloop()
