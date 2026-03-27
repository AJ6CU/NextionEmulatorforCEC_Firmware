#!/usr/bin/python3
"""
Frequency Spectrum

Displays an area of the Frequency showing signal strength

UI source file: frequencySpectrum.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
import frequencySpectrumui as baseui


#
# Manual user code
#

class frequencySpectrum(baseui.frequencySpectrumUI):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)


if __name__ == "__main__":
    root = tk.Tk()
    widget = frequencySpectrum(root)
    root.mainloop()
