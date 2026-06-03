#!/usr/bin/python3
"""
bandGraph

reuseable band graph object

UI source file: bandGraph.ui
"""
import tkinter as tk
import tkinter.ttk as ttk


def safe_i18n_translator(value):
    """i18n - Setup translator in derived class file"""
    return value


def safe_fo_callback(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def safe_image_loader(master, image_name: str):
    """Image loader - Setup image_loader in derived class file."""
    img = None
    try:
        img = tk.PhotoImage(file=image_name, master=master)
    except tk.TclError:
        pass
    return img


#
# Base class definition
#
class bandGraphUI(ttk.Labelframe):
    def __init__(
        self,
        master=None,
        *,
        translator=None,
        on_first_object_cb=None,
        data_pool=None,
        image_loader=None,
        **kw
    ):
        if translator is None:
            translator = safe_i18n_translator
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = safe_fo_callback

        super().__init__(master, **kw)

        self.bandGraph_Frame = ttk.Frame(self, name="bandgraph_frame")
        self.bandGraph_Frame.configure(
            height=200, style="NormalOutline.TFrame", width=200)
        # First object created
        on_first_object_cb(self.bandGraph_Frame)

        self.bandPlot_Canvas = tk.Canvas(
            self.bandGraph_Frame, name="bandplot_canvas")
        self.bandPlot_Canvas.configure(background="#0432ff", height=100)
        self.bandPlot_Canvas.pack(expand=True, fill="x", side="top")
        self.bandPlot_Canvas.bind("<Configure>", self.resizeCanvas_CB, add="+")
        self.bandStart_Scale = ttk.Scale(
            self.bandGraph_Frame, name="bandstart_scale")
        self.band0Start_VAR = tk.StringVar()
        self.bandStart_Scale.configure(
            from_=0,
            orient="horizontal",
            state="disabled",
            style="Custom.Horizontal.TScale",
            to=119,
            variable=self.band0Start_VAR)
        self.bandStart_Scale.pack(expand=True, fill="x", side="top")
        self.bandStart_Scale.configure(command=self.bandStart_CB)
        self.scan_Frame = ttk.Frame(self.bandGraph_Frame, name="scan_frame")
        self.scan_Frame.configure(height=200, style="Normal.TFrame", width=200)
        self.scanningRange_Label = ttk.Label(
            self.scan_Frame, name="scanningrange_label")
        self.scanningRange_VAR = tk.StringVar()
        self.scanningRange_Label.configure(
            style="Heading4b.TLabel",
            textvariable=self.scanningRange_VAR)
        self.scanningRange_Label.pack(side="left")
        self.bandRange_Label = ttk.Label(
            self.scan_Frame, name="bandrange_label")
        self.bandRange_VAR = tk.StringVar()
        self.bandRange_Label.configure(
            style="Heading4b.TLabel",
            textvariable=self.bandRange_VAR)
        self.bandRange_Label.pack(side="right")
        self.scan_Frame.pack(expand=True, fill="x", side="top")
        self.bandGraph_Frame.pack(expand=True, fill="x", side="top")
        self.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Select Band...',
            width=200)
        # Layout for 'bandLabelFrame' skipped in custom widget template.

    def resizeCanvas_CB(self, event=None):
        pass

    def bandStart_CB(self, scale_value):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = bandGraphUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
