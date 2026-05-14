#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


def i18n_translator_noop(value):
    """i18n - Setup translator in derived class file"""
    return value


def first_object_callback_noop(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def image_loader_default(master, image_name: str):
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
class bandScannerUI(tk.Toplevel):
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
            translator = i18n_translator_noop
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = image_loader_default
        if on_first_object_cb is None:
            on_first_object_cb = first_object_callback_noop

        super().__init__(master, **kw)

        self.bandScanner_Labelframe = ttk.Labelframe(
            self, name="bandscanner_labelframe")
        self.bandScanner_Labelframe.configure(
            height=200,
            style="Heading2.TLabelframe",
            text='Band Scanner\n',
            width=200)
        # First object created
        on_first_object_cb(self.bandScanner_Labelframe)

        self.frequencySpectrumFrame = ttk.Frame(
            self.bandScanner_Labelframe,
            name="frequencyspectrumframe")
        self.frequencySpectrumFrame.configure(
            height=180, style="Normal.TFrame", width=450)
        self.band0_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="band0_labelframe")
        self.band0_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Select Band...',
            width=200)
        self.band0Plot_Canvas = tk.Canvas(
            self.band0_Labelframe, name="band0plot_canvas")
        self.band0Plot_Canvas.configure(
            background="#0432ff", height=100, width=430)
        self.band0Plot_Canvas.grid(column=0, columnspan=3, row=1, sticky="ew")
        self.band0Plot_Canvas.bind(
            "<Configure>", self.resizeCanvas_CB, add="+")
        self.band0_Labelframe.grid(column=0, padx="8 0", row=0, sticky="ew")
        self.band0_Labelframe.columnconfigure(0, weight=1)
        self.band1_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="band1_labelframe")
        self.band1_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Select Band...',
            width=200)
        self.band1Plot_Canv = tk.Canvas(
            self.band1_Labelframe, name="band1plot_canv")
        self.band1Plot_Canv.configure(
            background="#0432ff", height=100, width=430)
        self.band1Plot_Canv.pack(expand=True, fill="both", side="top")
        self.band1_Labelframe.grid(column=0, padx="8 0", row=1, sticky="ew")
        self.band2_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="band2_labelframe")
        self.band2_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Select Band...',
            width=200)
        self.band2Plot_Canv = tk.Canvas(
            self.band2_Labelframe, name="band2plot_canv")
        self.band2Plot_Canv.configure(
            background="#0432ff", height=100, width=430)
        self.band2Plot_Canv.pack(expand=True, fill="both", side="top")
        self.band2_Labelframe.grid(column=0, padx="8 0", row=3, sticky="ew")
        self.freqTuneFrame = ttk.Frame(
            self.frequencySpectrumFrame,
            name="freqtuneframe")
        self.freqTuneFrame.configure(
            height=140, style="Normal.TFrame", width=200)
        self.frequencyTuning_Scale = tk.Scale(
            self.freqTuneFrame, name="frequencytuning_scale")
        self.frequencyTuning_VAR = tk.StringVar()
        self.frequencyTuning_Scale.configure(
            from_=0,
            length=500,
            orient="horizontal",
            relief="raised",
            resolution=1,
            showvalue=False,
            sliderlength=50,
            to=119,
            variable=self.frequencyTuning_VAR,
            width=30)
        self.frequencyTuning_Scale.pack(
            anchor="w",
            expand=True,
            fill="x",
            padx="10 0",
            pady="15 0",
            side="top")
        self.frequencyTuning_Scale.configure(command=self.frequencyTuning_CB)
        self.frequencyTuning_Scale.bind(
            "<ButtonPress-1>", self.frequencyTuningPress_CB, add="+")
        self.frequencyTuning_Scale.bind(
            "<ButtonRelease-1>",
            self.frequencyTuningRelease_CB,
            add="+")
        self.freqTuneFrame.grid(column=0, row=4, sticky="ew")
        self.frequencySpectrumFrame.grid(
            column=0, padx="10 0", row=0, sticky="ew")
        self.frequencySpectrumFrame.grid_anchor("e")
        self.frequencySpectrumFrame.rowconfigure(0, weight=1)
        self.frequencySpectrumFrame.rowconfigure(2, weight=1)
        self.frequencySpectrumFrame.columnconfigure(0, weight=1)
        self.controlFrame = ttk.Frame(
            self.bandScanner_Labelframe,
            name="controlframe")
        self.controlFrame.configure(
            height=140, style="Normal.TFrame", width=200)
        self.bandStatus_Frame = ttk.Frame(
            self.controlFrame, name="bandstatus_frame")
        self.bandStatus_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band1Select_Frame = ttk.Frame(
            self.bandStatus_Frame, name="band1select_frame")
        self.band1Select_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band1Select_Label = ttk.Label(
            self.band1Select_Frame, name="band1select_label")
        self.band1Select_Label.configure(
            style="Heading2b.TLabel", text='14.000.000')
        self.band1Select_Label.pack(side="left")
        self.band1GO_Button = ttk.Button(
            self.band1Select_Frame, name="band1go_button")
        self.band1GO_Button.configure(style="Button2b.TButton", text='QSY')
        self.band1GO_Button.pack(padx="10 0", side="top")
        def band1GO_Button_cmd_(): self.bandGo_CB("band1GO_Button")

        self.band1GO_Button.configure(command=band1GO_Button_cmd_)
        self.band1Select_Frame.pack(anchor="w", pady="70 0", side="top")
        self.band2Select_Frame = ttk.Frame(
            self.bandStatus_Frame, name="band2select_frame")
        self.band2Select_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band2Select_Label = ttk.Label(
            self.band2Select_Frame, name="band2select_label")
        self.band2Select_Label.configure(
            style="Heading2b.TLabel", text='14.000.000')
        self.band2Select_Label.pack(side="left")
        self.band2GO_Button = ttk.Button(
            self.band2Select_Frame, name="band2go_button")
        self.band2GO_Button.configure(style="Button2b.TButton", text='QSY')
        self.band2GO_Button.pack(padx="10 0", side="top")
        def band2GO_Button_cmd_(): self.bandGo_CB("band2GO_Button")

        self.band2GO_Button.configure(command=band2GO_Button_cmd_)
        self.band2Select_Frame.pack(anchor="w", pady="100 0", side="top")
        self.band3Select_Frame = ttk.Frame(
            self.bandStatus_Frame, name="band3select_frame")
        self.band3Select_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band3Select_Label = ttk.Label(
            self.band3Select_Frame, name="band3select_label")
        self.band3Select_Label.configure(
            style="Heading2b.TLabel", text='14.000.000')
        self.band3Select_Label.pack(side="left")
        self.band3GO_Button = ttk.Button(
            self.band3Select_Frame, name="band3go_button")
        self.band3GO_Button.configure(style="Button2b.TButton", text='QSY')
        self.band3GO_Button.pack(padx="10 0", side="top")
        def band3GO_Button_cmd_(): self.bandGo_CB("band3GO_Button")

        self.band3GO_Button.configure(command=band3GO_Button_cmd_)
        self.band3Select_Frame.pack(anchor="w", pady="100 0", side="top")
        self.bandStatus_Frame.pack(
            anchor="ne", expand=True, fill="x", side="top")
        self.bandSelectFrame = ttk.Frame(
            self.controlFrame, name="bandselectframe")
        self.bandSelectFrame.configure(
            height=200, style="NormalOutline.TFrame", width=200)
        label3 = ttk.Label(self.bandSelectFrame)
        label3.configure(
            justify="center",
            style="Heading2b.TLabel",
            text='Select Bands (max 3)')
        label3.pack(pady=10, side="top")
        self.bandCheckbox_Frame = ttk.Frame(
            self.bandSelectFrame, name="bandcheckbox_frame")
        self.bandCheckbox_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band160m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band160m_checkbox")
        self.band160m_Checked_VAR = tk.StringVar()
        self.band160m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='160M',
            variable=self.band160m_Checked_VAR)
        self.band160m_checkbox.grid(column=0, row=0)
        def band160m_checkbox_cmd_(): self.band_Checked_CB("band160m_checkbox")

        self.band160m_checkbox.configure(command=band160m_checkbox_cmd_)
        self.band80m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band80m_checkbox")
        self.ban80m_Checked_VAR = tk.StringVar()
        self.band80m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='80M',
            variable=self.ban80m_Checked_VAR)
        self.band80m_checkbox.grid(column=0, pady="15 0", row=1, sticky="w")
        def band80m_checkbox_cmd_(): self.band_Checked_CB("band80m_checkbox")

        self.band80m_checkbox.configure(command=band80m_checkbox_cmd_)
        self.band40m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band40m_checkbox")
        self.band40m_Checked_VAR = tk.StringVar()
        self.band40m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='40M',
            variable=self.band40m_Checked_VAR)
        self.band40m_checkbox.grid(column=0, pady="15 10", row=2, sticky="w")
        def band40m_checkbox_cmd_(): self.band_Checked_CB("band40m_checkbox")

        self.band40m_checkbox.configure(command=band40m_checkbox_cmd_)
        self.band30m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band30m_checkbox")
        self.band30m_Checked_VAR = tk.StringVar()
        self.band30m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='30M',
            variable=self.band30m_Checked_VAR)
        self.band30m_checkbox.grid(column=1, padx="10 0", row=0, sticky="w")
        def band30m_checkbox_cmd_(): self.band_Checked_CB("band30m_checkbox")

        self.band30m_checkbox.configure(command=band30m_checkbox_cmd_)
        self.band20m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band20m_checkbox")
        self.band20m_Checked_VAR = tk.StringVar()
        self.band20m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='20M',
            variable=self.band20m_Checked_VAR)
        self.band20m_checkbox.grid(
            column=1,
            padx="10 0",
            pady="15 0",
            row=1,
            sticky="w")

        def band20m_checkbox_cmd_(): self.band_Checked_CB("band20m_checkbox")

        self.band20m_checkbox.configure(command=band20m_checkbox_cmd_)
        self.band17m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band17m_checkbox")
        self.band17m_Checked_VAR = tk.StringVar()
        self.band17m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='17M',
            variable=self.band17m_Checked_VAR)
        self.band17m_checkbox.grid(
            column=1,
            padx="10 0",
            pady="15 10",
            row=2,
            sticky="w")

        def band17m_checkbox_cmd_(): self.band_Checked_CB("band17m_checkbox")

        self.band17m_checkbox.configure(command=band17m_checkbox_cmd_)
        self.band15m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band15m_checkbox")
        self.band15m_Checked_VAR = tk.StringVar()
        self.band15m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='15M',
            variable=self.band15m_Checked_VAR)
        self.band15m_checkbox.grid(column=2, padx="10 0", row=0, sticky="w")
        def band15m_checkbox_cmd_(): self.band_Checked_CB("band15m_checkbox")

        self.band15m_checkbox.configure(command=band15m_checkbox_cmd_)
        self.band12m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band12m_checkbox")
        self.band12m_Checked_VAR = tk.StringVar()
        self.band12m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='12M',
            variable=self.band12m_Checked_VAR)
        self.band12m_checkbox.grid(
            column=2,
            padx="10 0",
            pady="15 0",
            row=1,
            sticky="w")

        def band12m_checkbox_cmd_(): self.band_Checked_CB("band12m_checkbox")

        self.band12m_checkbox.configure(command=band12m_checkbox_cmd_)
        self.band10m_checkbox = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band10m_checkbox")
        self.band10m_Checked_VAR = tk.StringVar()
        self.band10m_checkbox.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='10M',
            variable=self.band10m_Checked_VAR)
        self.band10m_checkbox.grid(
            column=2,
            padx="10 0",
            pady="15 10",
            row=2,
            sticky="w")

        def band10m_checkbox_cmd_(): self.band_Checked_CB("band10m_checkbox")

        self.band10m_checkbox.configure(command=band10m_checkbox_cmd_)
        self.bandCheckbox_Frame.pack(side="top")
        self.bandSelectFrame.pack(
            anchor="ne",
            expand=True,
            fill="both",
            ipadx=5,
            ipady=5,
            padx="0 10",
            pady="55 10",
            side="left")
        self.controlFrame.grid(
            column=1,
            padx="10 0",
            row=0,
            rowspan=3,
            sticky="ew")
        self.closingFrame = ttk.Frame(
            self.bandScanner_Labelframe,
            name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.scan_Button = ttk.Button(self.closingFrame, name="scan_button")
        self.scan_Button.configure(
            style="Button2b.TButton", text='Scan', width=10)
        self.scan_Button.pack(padx="0 20", side="left")
        self.scan_Button.configure(command=self.scan_CB)
        self.close_Button = ttk.Button(self.closingFrame, name="close_button")
        self.close_Button.configure(
            style="Button2b.TButton", text='Close', width=10)
        self.close_Button.pack(side="left")
        self.close_Button.configure(command=self.close_CB)
        self.closingFrame.grid(column=0, columnspan=2, pady="20 0", row=1)
        self.bandScanner_Labelframe.pack(expand=True, fill="both", side="top")
        self.bandScanner_Labelframe.rowconfigure(0, uniform=1)
        self.bandScanner_Labelframe.columnconfigure(0, weight=1)
        self.configure(height=200, width=800)
        self.geometry("800x625")
        self.title("Frequency Spectrum")

    def resizeCanvas_CB(self, event=None):
        pass

    def frequencyTuning_CB(self, scale_value):
        pass

    def frequencyTuningPress_CB(self, event=None):
        pass

    def frequencyTuningRelease_CB(self, event=None):
        pass

    def bandGo_CB(self, widget_id):
        pass

    def band_Checked_CB(self, widget_id):
        pass

    def scan_CB(self):
        pass

    def close_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = bandScannerUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
