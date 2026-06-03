#!/usr/bin/python3
"""
Frequency Spectrum

Displays an area of the Frequency showing signal strength

UI source file: frequencySpectrum.ui
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
class frequencySpectrumUI(tk.Toplevel):
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

        self.frequencySpectrum_Labelframe = ttk.Labelframe(
            self, name="frequencyspectrum_labelframe")
        self.frequencySpectrum_Labelframe.configure(
            height=200,
            style="Heading2.TLabelframe",
            text='Frequency Spectrum\n',
            width=200)
        # First object created
        on_first_object_cb(self.frequencySpectrum_Labelframe)

        self.frequencySpectrumFrame = ttk.Frame(
            self.frequencySpectrum_Labelframe,
            name="frequencyspectrumframe")
        self.frequencySpectrumFrame.configure(
            height=180, style="Normal.TFrame", width=450)
        self.average_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="average_labelframe")
        self.average_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Average',
            width=200)
        self.frequencyPlotCanvas = tk.Canvas(
            self.average_Labelframe, name="frequencyplotcanvas")
        self.frequencyPlotCanvas.configure(
            background="#0432ff", height=160, width=430)
        self.frequencyPlotCanvas.grid(
            column=0, columnspan=3, row=1, sticky="ew")
        self.frequencyPlotCanvas.bind(
            "<Configure>", self.resizeCanvas_CB, add="+")
        self.average_Labelframe.grid(column=0, padx="8 0", row=0, sticky="ew")
        self.average_Labelframe.columnconfigure(0, weight=1)
        self.peak_Labelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="peak_labelframe")
        self.peak_Labelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Peak',
            width=200)
        self.waterfall_Canvas = tk.Canvas(
            self.peak_Labelframe, name="waterfall_canvas")
        self.waterfall_Canvas.configure(
            background="#0432ff", height=160, width=430)
        self.waterfall_Canvas.pack(expand=True, fill="both", side="top")
        self.peak_Labelframe.grid(column=0, padx="8 0", row=1, sticky="ew")
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
        self.frequencyTuning_Scale.grid(
            column=0, padx="10 0", row=0, sticky="ew")
        self.frequencyTuning_Scale.configure(command=self.frequencyTuning_CB)
        self.frequencyTuning_Scale.bind(
            "<ButtonPress-1>", self.frequencyTuningPress_CB, add="+")
        self.frequencyTuning_Scale.bind(
            "<ButtonRelease-1>",
            self.frequencyTuningRelease_CB,
            add="+")
        self.frequencyRange_Frame = ttk.Frame(
            self.freqTuneFrame, name="frequencyrange_frame")
        self.frequencyRange_Frame.configure(
            height=40, style="Normal.TFrame", width=200)
        self.startFrequency_Label = ttk.Label(
            self.frequencyRange_Frame, name="startfrequency_label")
        self.startFrequency_VAR = tk.StringVar(value='0')
        self.startFrequency_Label.configure(
            foreground="black",
            style="Heading2b.TLabel",
            text='0',
            textvariable=self.startFrequency_VAR)
        self.startFrequency_Label.pack(side="left")
        self.endFrequency_Label = ttk.Label(
            self.frequencyRange_Frame, name="endfrequency_label")
        self.stopFrequency_VAR = tk.StringVar(value='120000')
        self.endFrequency_Label.configure(
            foreground="black",
            style="Heading2b.TLabel",
            text='120000',
            textvariable=self.stopFrequency_VAR)
        self.endFrequency_Label.pack(side="right")
        self.frequencyRange_Frame.grid(column=0, row=1, sticky="ew")
        self.freqTuneFrame.grid(column=0, row=2, sticky="ew")
        self.freqTuneFrame.columnconfigure(0, weight=1)
        self.frequencySpectrumFrame.grid(
            column=0, padx="10 0", row=0, sticky="ew")
        self.frequencySpectrumFrame.grid_anchor("e")
        self.frequencySpectrumFrame.rowconfigure(0, weight=1)
        self.frequencySpectrumFrame.rowconfigure(2, weight=1)
        self.frequencySpectrumFrame.columnconfigure(0, weight=1)
        self.controlFrame = ttk.Frame(
            self.frequencySpectrum_Labelframe,
            name="controlframe")
        self.controlFrame.configure(
            height=140, style="Normal.TFrame", width=200)
        self.optionFrame = ttk.Frame(self.controlFrame, name="optionframe")
        self.optionFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.bandwidthControlFrame = ttk.Frame(
            self.optionFrame, name="bandwidthcontrolframe")
        self.bandwidthControlFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.bandwidth_Label = ttk.Label(
            self.bandwidthControlFrame,
            name="bandwidth_label")
        self.bandwidth_Label.configure(
            style="Heading2b.TLabel",
            text='Bandwidth (Hz)')
        self.bandwidth_Label.grid(column=0, row=0)
        self.repeat_Label = ttk.Label(
            self.bandwidthControlFrame,
            name="repeat_label")
        self.repeat_Label.configure(style="Heading2b.TLabel", text='Repeat')
        self.repeat_Label.grid(column=1, row=0)
        self.bandwidth_Menubutton = ttk.Menubutton(
            self.bandwidthControlFrame, name="bandwidth_menubutton")
        self.bandwidthSelected_VAR = tk.StringVar()
        self.bandwidth_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.bandwidthSelected_VAR,
            width=8)
        self.bandwidth_Menu = tk.Menu(
            self.bandwidth_Menubutton,
            name="bandwidth_menu")
        self.bandwidth_Menu.configure(tearoff=False)
        self.bandwidth_Menu.add(
            "command",
            command=self.select_60k_CB,
            font="{Arial} 36 {}",
            label='60,000',
            state="normal")
        self.bandwidth_Menu.add(
            "command",
            command=self.select_120k_CB,
            font="{Arial} 36 {}",
            label='120,000',
            state="normal")
        self.bandwidth_Menu.add(
            "command",
            command=self.select_240k_CB,
            font="{Arial} 36 {}",
            label='240,000',
            state="normal")
        self.bandwidth_Menu.add(
            "command",
            command=self.select_360k_CB,
            font="{Arial} 36 {}",
            label='360,000',
            state="normal")
        self.bandwidth_Menu.add(
            "command",
            command=self.select_480k_CB,
            font="{Arial} 36 {}",
            label='480,000',
            state="normal")
        self.bandwidth_Menubutton.configure(menu=self.bandwidth_Menu)
        self.bandwidth_Menubutton.grid(padx="0 20", row=1, sticky="w")
        self.repeat_Menubutton = ttk.Menubutton(
            self.bandwidthControlFrame, name="repeat_menubutton")
        self.repeat_VAR = tk.StringVar()
        self.repeat_Menubutton.configure(
            style="Heading0.TMenubutton",
            textvariable=self.repeat_VAR,
            width=3)
        self.repeat_Menu = tk.Menu(self.repeat_Menubutton, name="repeat_menu")
        self.repeat_Menu.configure(tearoff=False)
        self.repeat_Menu.add(
            "command",
            command=self.select_Repeat_1x_CB,
            font="{Arial} 36 {}",
            label='1',
            state="normal")
        self.repeat_Menu.add(
            "command",
            command=self.select_Repeat_5x_CB,
            font="{Arial} 36 {}",
            label='5',
            state="normal")
        self.repeat_Menu.add(
            "command",
            command=self.select_Repeat_10x_CB,
            font="{Arial} 36 {}",
            label='10',
            state="normal")
        self.repeat_Menu.add(
            "command",
            command=self.select_Repeat_15x_CB,
            font="{Arial} 36 {}",
            label='15',
            state="normal")
        self.repeat_Menu.add(
            "command",
            command=self.select_Repeat_20x_CB,
            font="{Arial} 36 {}",
            label='20',
            state="normal")
        self.repeat_Menu.add(
            "command",
            command=self.select_Repeat_50x_CB,
            font="{Arial} 36 {}",
            label='50',
            state="normal")
        self.repeat_Menubutton.configure(menu=self.repeat_Menu)
        self.repeat_Menubutton.grid(column=1, row=1)
        self.sampleSize_Label = ttk.Label(
            self.bandwidthControlFrame,
            name="samplesize_label")
        self.sampleSize_Label.configure(
            anchor="e",
            justify="center",
            style="Heading2b.TLabel",
            text='Sample Size(Hz)')
        self.sampleSize_Label.grid(column=0, pady="20 0", row=2)
        self.remaining_Label = ttk.Label(
            self.bandwidthControlFrame,
            name="remaining_label")
        self.remaining_Label.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='Remaining')
        self.remaining_Label.grid(column=1, pady="20 0", row=2)
        self.calculatedSampleSize_Label = ttk.Label(
            self.bandwidthControlFrame, name="calculatedsamplesize_label")
        self.calculatedSampleSize_VAR = tk.StringVar(value='1000')
        self.calculatedSampleSize_Label.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='1000',
            textvariable=self.calculatedSampleSize_VAR)
        self.calculatedSampleSize_Label.grid(column=0, row=3)
        self.remainingCount_Label = ttk.Label(
            self.bandwidthControlFrame, name="remainingcount_label")
        self.remainingCount_VAR = tk.StringVar(value='10')
        self.remainingCount_Label.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='10',
            textvariable=self.remainingCount_VAR)
        self.remainingCount_Label.grid(column=1, row=3)
        self.bandwidthControlFrame.pack(
            anchor="nw", expand=True, fill="x", side="top")
        self.optionFrame.pack(
            anchor="ne",
            expand=True,
            fill="x",
            padx="0 20",
            pady="30 0",
            side="top")
        self.currentFreqFrame = ttk.Frame(
            self.controlFrame, name="currentfreqframe")
        self.currentFreqFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.freqLabel = ttk.Label(self.currentFreqFrame, name="freqlabel")
        self.freqLabel.configure(style="Heading1b.TLabel", text='Freq:')
        self.freqLabel.pack(side="left")
        self.currentFrequency_Label = ttk.Label(
            self.currentFreqFrame, name="currentfrequency_label")
        self.currentFrequency_VAR = tk.StringVar(value='0')
        self.currentFrequency_Label.configure(
            style="Heading1b.TLabel",
            text='0',
            textvariable=self.currentFrequency_VAR)
        self.currentFrequency_Label.pack(padx=10, side="left")
        self.currentFreqFrame.pack(pady="100 0", side="left")
        self.controlFrame.grid(
            column=1,
            padx="10 0",
            pady="100 0",
            row=0,
            rowspan=3,
            sticky="ne")
        self.closingFrame = ttk.Frame(
            self.frequencySpectrum_Labelframe,
            name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.startStop_Button = ttk.Button(
            self.closingFrame, name="startstop_button")
        self.startStopSpectrum_VAR = tk.StringVar(value='Scan')
        self.startStop_Button.configure(
            style="Button2b.TButton",
            text='Scan',
            textvariable=self.startStopSpectrum_VAR,
            width=10)
        self.startStop_Button.grid(padx="0 15", row=0)
        self.startStop_Button.configure(command=self.startSpectrum_CB)
        self.recenter_Button = ttk.Button(
            self.closingFrame, name="recenter_button")
        self.recenter_Button.configure(
            style="Button2b.TButton", text='Center', width=10)
        self.recenter_Button.grid(column=1, padx="0 15", row=0)
        self.recenter_Button.configure(command=self.recenter_CB)
        self.applyClose_Button = ttk.Button(
            self.closingFrame, name="applyclose_button")
        self.closeApply_Button_VAR = tk.StringVar(value='Close')
        self.applyClose_Button.configure(
            style="Button2b.TButton",
            text='Close',
            textvariable=self.closeApply_Button_VAR,
            width=10)
        self.applyClose_Button.grid(column=2, padx="0 15", row=0)
        self.applyClose_Button.configure(command=self.applyClose_CB)
        self.cancel_Button = ttk.Button(
            self.closingFrame, name="cancel_button")
        self.cancel_Button.configure(
            style="Button2b.TButton", text='Cancel', width=10)
        self.cancel_Button.grid(column=3, row=0)
        self.cancel_Button.configure(command=self.cancel_CB)
        self.closingFrame.grid(
            column=0,
            columnspan=2,
            pady="20 15",
            row=1,
            sticky="ew")
        self.closingFrame.grid_anchor("center")
        self.frequencySpectrum_Labelframe.pack(
            expand=True, fill="both", side="top")
        self.frequencySpectrum_Labelframe.rowconfigure(0, uniform=1)
        self.frequencySpectrum_Labelframe.columnconfigure(0, weight=1)
        self.title("Frequency Spectrum")
        # Layout for 'frequencySpectrum_Window' skipped in custom widget
        # template.

    def resizeCanvas_CB(self, event=None):
        pass

    def frequencyTuning_CB(self, scale_value):
        pass

    def frequencyTuningPress_CB(self, event=None):
        pass

    def frequencyTuningRelease_CB(self, event=None):
        pass

    def select_60k_CB(self):
        pass

    def select_120k_CB(self):
        pass

    def select_240k_CB(self):
        pass

    def select_360k_CB(self):
        pass

    def select_480k_CB(self):
        pass

    def select_Repeat_1x_CB(self):
        pass

    def select_Repeat_5x_CB(self):
        pass

    def select_Repeat_10x_CB(self):
        pass

    def select_Repeat_15x_CB(self):
        pass

    def select_Repeat_20x_CB(self):
        pass

    def select_Repeat_50x_CB(self):
        pass

    def startSpectrum_CB(self):
        pass

    def recenter_CB(self):
        pass

    def applyClose_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = frequencySpectrumUI(root)
    root.mainloop()
