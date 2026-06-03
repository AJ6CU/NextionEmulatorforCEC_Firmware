#!/usr/bin/python3
"""
Progress Warning Dialog

Just pops up a warning dialog

UI source file: progress_warning.ui
"""
import tkinter as tk
import tkinter.ttk as ttk


class delayWarning(tk.Toplevel):
    """Your widget direct subclass.

    Only simple properties will be configured.
    No commands, no bindings.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        frame1 = ttk.Frame(self)
        frame1.configure(height=200, style="Normal.TFrame", width=200)
        label1 = ttk.Label(frame1)
        label1.configure(
            justify="center",
            style="Heading1bi.TLabel",
            text='Loading...\n\nThis could take several seconds...')
        label1.pack(padx=10, pady=10, side="top")
        progressbar1 = ttk.Progressbar(frame1)
        self.progressBarStatus_VAR = tk.StringVar()
        progressbar1.configure(
            mode="indeterminate",
            orient="horizontal",
            variable=self.progressBarStatus_VAR)
        progressbar1.pack(expand=True, fill="x", padx=10, pady=10, side="top")
        frame1.pack(expand=True, fill="both", side="top")
        self.configure(height=200, width=200)
        self.title("Warning... Delay")
        # Layout for 'delay_warning' skipped in custom widget template.


if __name__ == "__main__":
    root = tk.Tk()
    widget = delayWarning(root)
    root.mainloop()
