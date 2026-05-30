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

        self.warningFrame = ttk.Frame(self, name="warningframe")
        self.warningFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.warningLabel = ttk.Label(self.warningFrame, name="warninglabel")
        self.warningLabel_VAR = tk.StringVar(
            value='Loading...\n\nThis could take several seconds...')
        self.warningLabel.configure(
            anchor="w",
            justify="center",
            style="Heading1bi.TLabel",
            text='Loading...\n\nThis could take several seconds...',
            textvariable=self.warningLabel_VAR)
        self.warningLabel.pack(padx=10, pady=10, side="top")
        self.warningFrame.pack(expand=True, fill="both", side="top")
        self.configure(height=200, width=200)
        self.title("Warning... Delay")
        # Layout for 'delay_warning' skipped in custom widget template.


if __name__ == "__main__":
    root = tk.Tk()
    widget = delayWarning(root)
    root.mainloop()
