#!/usr/bin/python3
"""
Progress Warning Dialog

Just pops up a warning dialog

UI source file: progress_warning.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import delayWarningui as baseui


#
# Manual user code
#

class delayWarning(baseui.delayWarningUI):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)


if __name__ == "__main__":
    root = tk.Tk()
    widget = delayWarning(root)
    root.mainloop()
