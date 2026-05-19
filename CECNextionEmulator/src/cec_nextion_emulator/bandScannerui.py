#!/usr/bin/python3
"""
Band Scanner

Scans up to three selected bands for signals.

UI source file: bandScanner.ui
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
            translator = safe_i18n_translator
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = safe_fo_callback

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
        self.band0Plot_Canvas.grid(column=0, columnspan=3, row=0, sticky="ew")
        self.band0Plot_Canvas.bind(
            "<Configure>", self.resizeCanvas_CB, add="+")
        self.band0Start_Scale = ttk.Scale(
            self.band0_Labelframe, name="band0start_scale")
        self.band0Start_VAR = tk.StringVar()
        self.band0Start_Scale.configure(
            from_=0,
            orient="horizontal",
            to=119,
            variable=self.band0Start_VAR)
        self.band0Start_Scale.grid(column=0, row=1, sticky="ew")
        self.band0_Labelframe.grid(column=0, padx="8 0", row=0, sticky="ew")
        self.band0_Labelframe.columnconfigure(0, weight=1)
        self.band1_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="band1_labelframe")
        self.band1_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Select Band...',
            width=200)
        self.band1Plot_Canvas = tk.Canvas(
            self.band1_Labelframe, name="band1plot_canvas")
        self.band1Plot_Canvas.configure(
            background="#0432ff", height=100, width=430)
        self.band1Plot_Canvas.grid(column=0, columnspan=3, row=0, sticky="ew")
        self.band1Start_Scale = ttk.Scale(
            self.band1_Labelframe, name="band1start_scale")
        self.band1Start_VAR = tk.StringVar()
        self.band1Start_Scale.configure(
            from_=0,
            orient="horizontal",
            to=119,
            variable=self.band1Start_VAR)
        self.band1Start_Scale.grid(column=0, row=1, sticky="ew")
        self.band1_Labelframe.grid(column=0, padx="8 0", row=1, sticky="ew")
        self.band1_Labelframe.columnconfigure(0, weight=1)
        self.band2_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="band2_labelframe")
        self.band2_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Select Band...',
            width=200)
        self.band2Plot_Canvas = tk.Canvas(
            self.band2_Labelframe, name="band2plot_canvas")
        self.band2Plot_Canvas.configure(
            background="#0432ff", height=100, width=430)
        self.band2Plot_Canvas.grid(column=0, columnspan=3, row=0, sticky="ew")
        self.band2Start_Scale = ttk.Scale(
            self.band2_Labelframe, name="band2start_scale")
        self.band2Start_VAR = tk.StringVar()
        self.band2Start_Scale.configure(
            from_=0,
            orient="horizontal",
            to=119,
            variable=self.band2Start_VAR)
        self.band2Start_Scale.grid(sticky="ew")
        self.band2_Labelframe.grid(column=0, padx="8 0", row=2, sticky="ew")
        self.band2_Labelframe.columnconfigure(0, weight=1)
        self.freqTuneFrame = ttk.Frame(
            self.frequencySpectrumFrame,
            name="freqtuneframe")
        self.freqTuneFrame.configure(
            height=140, style="Normal.TFrame", width=200)
        self.frequencyTuning_Scale = tk.Scale(
            self.freqTuneFrame, name="frequencytuning_scale")
        self.frequencyTuning_VAR = tk.StringVar()
        self.frequencyTuning_Scale.configure(
            digits=0,
            from_=0,
            length=500,
            orient="horizontal",
            relief="raised",
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
        self.frequencyTuning_Scale.bind(
            "<ButtonRelease-1>",
            self.frequencyTuningRelease_CB,
            add="+")
        self.freqTuneFrame.grid(column=0, row=3, sticky="ew")
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
        self.band0Select_Frame = ttk.Frame(
            self.bandStatus_Frame, name="band0select_frame")
        self.band0Select_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band0Frequency_Label = ttk.Label(
            self.band0Select_Frame, name="band0frequency_label")
        self.band0Frequency_VAR = tk.StringVar(value='14.032.000')
        self.band0Frequency_Label.configure(
            style="Heading2b.TLabel",
            text='14.032.000',
            textvariable=self.band0Frequency_VAR,
            width=10)
        self.band0Frequency_Label.grid(column=0, row=0)
        self.band0GO_Button = ttk.Button(
            self.band0Select_Frame, name="band0go_button")
        self.band0GO_Button.configure(style="Button2b.TButton", text='QSY')
        self.band0GO_Button.grid(column=1, row=0)
        def band0GO_Button_cmd_(): self.bandGo_CB("band0GO_Button")

        self.band0GO_Button.configure(command=band0GO_Button_cmd_)
        self.band1Boundaries_Frame = ttk.Frame(
            self.band0Select_Frame, name="band1boundaries_frame")
        self.band1Boundaries_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band0Start_Label = ttk.Label(
            self.band1Boundaries_Frame,
            name="band0start_label")
        self.band0Start_Label.configure(
            style="Heading4b.TLabel", text='Start:')
        self.band0Start_Label.grid(column=0, row=0, sticky="e")
        self.band0StartFrequency_Label = ttk.Label(
            self.band1Boundaries_Frame, name="band0startfrequency_label")
        self.band0StartFrequency_Label.configure(
            style="Heading4b.TLabel", text='14.000.000')
        self.band0StartFrequency_Label.grid(column=1, row=0, sticky="w")
        self.band0End_Label = ttk.Label(
            self.band1Boundaries_Frame,
            name="band0end_label")
        self.band0End_Label.configure(style="Heading4b.TLabel", text='End:')
        self.band0End_Label.grid(column=0, row=1, sticky="e")
        self.band0EndFrequency_Label = ttk.Label(
            self.band1Boundaries_Frame, name="band0endfrequency_label")
        self.band0EndFrequency_Label.configure(
            style="Heading4b.TLabel", text='14.240.000')
        self.band0EndFrequency_Label.grid(column=1, row=1, sticky="w")
        self.band1Boundaries_Frame.grid(
            column=0, columnspan=2, pady="10 0", row=3, sticky="w")
        self.band0Select_Frame.pack(anchor="w", pady="70 0", side="top")
        self.band1Select_Frame = ttk.Frame(
            self.bandStatus_Frame, name="band1select_frame")
        self.band1Select_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band1Frequency_Label = ttk.Label(
            self.band1Select_Frame, name="band1frequency_label")
        self.band1Frequency_VAR = tk.StringVar()
        self.band1Frequency_Label.configure(
            style="Heading2b.TLabel",
            textvariable=self.band1Frequency_VAR,
            width=10)
        self.band1Frequency_Label.grid(column=0, row=0)
        self.band1GO_Button = ttk.Button(
            self.band1Select_Frame, name="band1go_button")
        self.band1GO_Button.configure(style="Button2b.TButton", text='QSY')
        self.band1GO_Button.grid(column=1, row=0)
        def band1GO_Button_cmd_(): self.bandGo_CB("band1GO_Button")

        self.band1GO_Button.configure(command=band1GO_Button_cmd_)
        self.band2Boundaries_Frame = ttk.Frame(
            self.band1Select_Frame, name="band2boundaries_frame")
        self.band2Boundaries_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band1Start_Label = ttk.Label(
            self.band2Boundaries_Frame,
            name="band1start_label")
        self.band1Start_Label.configure(
            style="Heading4b.TLabel", text='Start:')
        self.band1Start_Label.grid(column=0, row=0, sticky="e")
        self.band1StartFrequency_Label = ttk.Label(
            self.band2Boundaries_Frame, name="band1startfrequency_label")
        self.band1StartFrequency_Label.configure(
            style="Heading4b.TLabel", text='14.000.000')
        self.band1StartFrequency_Label.grid(column=1, row=0, sticky="w")
        self.band1End_Label = ttk.Label(
            self.band2Boundaries_Frame,
            name="band1end_label")
        self.band1End_Label.configure(style="Heading4b.TLabel", text='End:')
        self.band1End_Label.grid(column=0, row=1, sticky="e")
        self.band1EndFrequency_Label = ttk.Label(
            self.band2Boundaries_Frame, name="band1endfrequency_label")
        self.band1EndFrequency_Label.configure(
            style="Heading4b.TLabel", text='14.240.000')
        self.band1EndFrequency_Label.grid(column=1, row=1, sticky="w")
        self.band2Boundaries_Frame.grid(
            column=0, columnspan=2, pady="10 0", row=3, sticky="w")
        self.band1Select_Frame.pack(anchor="w", pady="70 0", side="top")
        self.band2Select_Frame = ttk.Frame(
            self.bandStatus_Frame, name="band2select_frame")
        self.band2Select_Frame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.band2Frequency_Label = ttk.Label(
            self.band2Select_Frame, name="band2frequency_label")
        self.band2Frequency_VAR = tk.StringVar()
        self.band2Frequency_Label.configure(
            style="Heading2b.TLabel",
            textvariable=self.band2Frequency_VAR,
            width=10)
        self.band2Frequency_Label.grid(column=0, row=0)
        self.band2GO_Button = ttk.Button(
            self.band2Select_Frame, name="band2go_button")
        self.band2GO_Button.configure(style="Button2b.TButton", text='QSY')
        self.band2GO_Button.grid(column=1, row=0)
        def band2GO_Button_cmd_(): self.bandGo_CB("band2GO_Button")

        self.band2GO_Button.configure(command=band2GO_Button_cmd_)
        self.frame4 = ttk.Frame(self.band2Select_Frame, name="frame4")
        self.frame4.configure(height=200, style="Normal.TFrame", width=200)
        self.band2Start_Label = ttk.Label(self.frame4, name="band2start_label")
        self.band2Start_Label.configure(
            style="Heading4b.TLabel", text='Start:')
        self.band2Start_Label.grid(column=0, row=0, sticky="e")
        self.band2StartFrequency_Label = ttk.Label(
            self.frame4, name="band2startfrequency_label")
        self.band2StartFrequency_Label.configure(
            style="Heading4b.TLabel", text='14.000.000')
        self.band2StartFrequency_Label.grid(column=1, row=0, sticky="w")
        self.band2End_Label = ttk.Label(self.frame4, name="band2end_label")
        self.band2End_Label.configure(style="Heading4b.TLabel", text='End:')
        self.band2End_Label.grid(column=0, row=1, sticky="e")
        self.band2EndFrequency_Label = ttk.Label(
            self.frame4, name="band2endfrequency_label")
        self.band2EndFrequency_Label.configure(
            style="Heading4b.TLabel", text='14.240.000')
        self.band2EndFrequency_Label.grid(column=1, row=1, sticky="w")
        self.frame4.grid(
            column=0,
            columnspan=2,
            pady="10 0",
            row=3,
            sticky="w")
        self.band2Select_Frame.pack(anchor="w", pady="100 0", side="top")
        self.bandStatus_Frame.pack(
            anchor="ne",
            expand=True,
            fill="x",
            padx="0 20",
            side="top")
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
        self.Band160m = ttk.Checkbutton(
            self.bandCheckbox_Frame, name="band160m")
        self.Band160m_Checked_VAR = tk.StringVar()
        self.Band160m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='160M',
            variable=self.Band160m_Checked_VAR)
        self.Band160m.grid(column=0, row=0)
        def Band160m_cmd_(): self.band_Checked_CB("Band160m")

        self.Band160m.configure(command=Band160m_cmd_)
        self.Band80m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band80m")
        self.Band80m_Checked_VAR = tk.StringVar()
        self.Band80m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='80M',
            variable=self.Band80m_Checked_VAR)
        self.Band80m.grid(column=0, pady="15 0", row=1, sticky="w")
        def Band80m_cmd_(): self.band_Checked_CB("Band80m")

        self.Band80m.configure(command=Band80m_cmd_)
        self.Band40m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band40m")
        self.Band40m_Checked_VAR = tk.StringVar()
        self.Band40m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='40M',
            variable=self.Band40m_Checked_VAR)
        self.Band40m.grid(column=0, pady="15 10", row=2, sticky="w")
        def Band40m_cmd_(): self.band_Checked_CB("Band40m")

        self.Band40m.configure(command=Band40m_cmd_)
        self.Band30m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band30m")
        self.Band30m_Checked_VAR = tk.StringVar()
        self.Band30m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='30M',
            variable=self.Band30m_Checked_VAR)
        self.Band30m.grid(column=1, padx="10 0", row=0, sticky="w")
        def Band30m_cmd_(): self.band_Checked_CB("Band30m")

        self.Band30m.configure(command=Band30m_cmd_)
        self.Band20m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band20m")
        self.Band20m_Checked_VAR = tk.StringVar()
        self.Band20m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='20M',
            variable=self.Band20m_Checked_VAR)
        self.Band20m.grid(
            column=1,
            padx="10 0",
            pady="15 0",
            row=1,
            sticky="w")

        def Band20m_cmd_(): self.band_Checked_CB("Band20m")

        self.Band20m.configure(command=Band20m_cmd_)
        self.Band17m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band17m")
        self.Band17m_Checked_VAR = tk.StringVar()
        self.Band17m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='17M',
            variable=self.Band17m_Checked_VAR)
        self.Band17m.grid(
            column=1,
            padx="10 0",
            pady="15 10",
            row=2,
            sticky="w")

        def Band17m_cmd_(): self.band_Checked_CB("Band17m")

        self.Band17m.configure(command=Band17m_cmd_)
        self.Band15m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band15m")
        self.Band15m_Checked_VAR = tk.StringVar()
        self.Band15m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='15M',
            variable=self.Band15m_Checked_VAR)
        self.Band15m.grid(column=2, padx="10 0", row=0, sticky="w")
        def Band15m_cmd_(): self.band_Checked_CB("Band15m")

        self.Band15m.configure(command=Band15m_cmd_)
        self.Band12m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band12m")
        self.Band12m_Checked_VAR = tk.StringVar()
        self.Band12m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='12M',
            variable=self.Band12m_Checked_VAR)
        self.Band12m.grid(
            column=2,
            padx="10 0",
            pady="15 0",
            row=1,
            sticky="w")

        def Band12m_cmd_(): self.band_Checked_CB("Band12m")

        self.Band12m.configure(command=Band12m_cmd_)
        self.Band10m = ttk.Checkbutton(self.bandCheckbox_Frame, name="band10m")
        self.Band10m_Checked_VAR = tk.StringVar()
        self.Band10m.configure(
            offvalue=0,
            onvalue=1,
            style="Checkbox2b.TCheckbutton",
            text='10M',
            variable=self.Band10m_Checked_VAR)
        self.Band10m.grid(
            column=2,
            padx="10 0",
            pady="15 10",
            row=2,
            sticky="w")

        def Band10m_cmd_(): self.band_Checked_CB("Band10m")

        self.Band10m.configure(command=Band10m_cmd_)
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
        self.scan_Button_VAR = tk.StringVar(value='Scan')
        self.scan_Button.configure(
            style="Button2b.TButton",
            text='Scan',
            textvariable=self.scan_Button_VAR,
            width=10)
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
        self.geometry("800x675")
        self.title("Frequency Spectrum")
        # Layout for 'bandScanner_Toplevel' skipped in custom widget template.

    def resizeCanvas_CB(self, event=None):
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
    root.mainloop()
