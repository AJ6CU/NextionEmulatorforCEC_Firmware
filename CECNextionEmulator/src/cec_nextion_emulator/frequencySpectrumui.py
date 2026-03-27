#!/usr/bin/python3
"""
Frequency Spectrum

Displays an area of the Frequency showing signal strength

UI source file: frequencySpectrum.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.combobox import Combobox


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
            height=180, style="Normal.TFrame", width=200)
        self.magnitudeLabelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="magnitudelabelframe")
        self.magnitudeLabelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Magnitude',
            width=200)
        self.frequencyPlotCanvas = tk.Canvas(
            self.magnitudeLabelframe, name="frequencyplotcanvas")
        self.frequencyPlotCanvas.configure(
            background="#0432ff", height=160, width=480)
        self.frequencyPlotCanvas.pack(
            expand=True, fill="both", padx="5 0", side="top")
        self.magnitudeLabelframe.grid(column=0, row=0)
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
            state="normal",
            to=100,
            variable=self.frequencyTuning_VAR,
            width=30)
        self.frequencyTuning_Scale.pack(pady="15 0", side="top")
        self.frequencyTuning_Scale.configure(command=self.frequencyTuning_CB)
        self.frequencyRange_Frame = ttk.Frame(
            self.freqTuneFrame, name="frequencyrange_frame")
        self.frequencyRange_Frame.configure(
            height=40, style="Normal.TFrame", width=200)
        self.startFrequency_Label = ttk.Label(
            self.frequencyRange_Frame, name="startfrequency_label")
        self.startFrequency_VAR = tk.StringVar(value='0')
        self.startFrequency_Label.configure(
            style="Heading2b.TLabel",
            text='0',
            textvariable=self.startFrequency_VAR)
        self.startFrequency_Label.pack(side="left")
        self.endFrequency_Label = ttk.Label(
            self.frequencyRange_Frame, name="endfrequency_label")
        self.endFrequency_VAR = tk.StringVar(value='120000')
        self.endFrequency_Label.configure(
            style="Heading2b.TLabel",
            text='120000',
            textvariable=self.endFrequency_VAR)
        self.endFrequency_Label.pack(side="right")
        self.frequencyRange_Frame.pack(
            expand=True, fill="x", pady="0 10", side="top")
        self.freqTuneFrame.grid(column=0, row=1, sticky="w")
        self.waterfallLabelframe = ttk.Labelframe(
            self.frequencySpectrumFrame, name="waterfalllabelframe")
        self.waterfallLabelframe.configure(
            height=200,
            style="Heading3.TLabelframe",
            text='Waterfall',
            width=200)
        self.watefall_Canvas = tk.Canvas(
            self.waterfallLabelframe, name="watefall_canvas")
        self.watefall_Canvas.configure(
            background="#0432ff", height=160, width=480)
        self.watefall_Canvas.pack(
            expand=True,
            fill="both",
            padx="10 0",
            side="top")
        self.waterfallLabelframe.grid(column=0, row=2)
        self.frequencySpectrumFrame.grid(
            column=0, padx="10 0", row=0, sticky="w")
        self.controlFrame = ttk.Frame(
            self.frequencySpectrum_Labelframe,
            name="controlframe")
        self.controlFrame.configure(
            height=140, style="Normal.TFrame", width=200)
        self.optionFrame = ttk.Frame(self.controlFrame, name="optionframe")
        self.optionFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.repeatControlFrame = ttk.Frame(
            self.optionFrame, name="repeatcontrolframe")
        self.repeatControlFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.repeat_Label = ttk.Label(
            self.repeatControlFrame, name="repeat_label")
        self.repeat_Label.configure(style="Heading2b.TLabel", text='Repeat')
        self.repeat_Label.grid(column=0, row=0, sticky="w")
        self.remaining_Label = ttk.Label(
            self.repeatControlFrame, name="remaining_label")
        self.remaining_Label.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='Remaining',
            width=10)
        self.remaining_Label.grid(column=1, padx="5 0", row=0, sticky="e")
        self.repeat_Combobox = Combobox(
            self.repeatControlFrame, name="repeat_combobox")
        self.repeat_VAR = tk.StringVar()
        self.repeat_Combobox.configure(
            keyvariable=self.repeat_VAR,
            style="ComboBox1.TCombobox",
            values='1x 5x 10x 15x 20x 50x Cont.',
            width=7)
        self.repeat_Combobox.grid(column=0, row=1, sticky="w")
        self.remainingCount_Label = ttk.Label(
            self.repeatControlFrame, name="remainingcount_label")
        self.remainingCount_VAR = tk.StringVar(value='10')
        self.remainingCount_Label.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='10',
            textvariable=self.remainingCount_VAR,
            width=8)
        self.remainingCount_Label.grid(column=1, padx="5 0", row=1, sticky="e")
        self.repeatControlFrame.pack(
            anchor="nw",
            expand=True,
            fill="x",
            pady="20 0",
            side="top")
        self.bandwidthControlFrame = ttk.Frame(
            self.optionFrame, name="bandwidthcontrolframe")
        self.bandwidthControlFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.bandwidth_Label = ttk.Label(
            self.bandwidthControlFrame,
            name="bandwidth_label")
        self.bandwidth_Label.configure(
            style="Heading2b.TLabel",
            text='Bandwidth (kHz)')
        self.bandwidth_Label.grid(column=0, row=0, sticky="w")
        self.bandwidth_Combobox = Combobox(
            self.bandwidthControlFrame,
            name="bandwidth_combobox")
        self.bandwidth_VAR = tk.StringVar()
        self.bandwidth_Combobox.configure(
            keyvariable=self.bandwidth_VAR,
            style="ComboBox1.TCombobox",
            values='1x 5x 10x 15x 20x 50x Cont.',
            width=7)
        self.bandwidth_Combobox.grid(column=0, row=1, sticky="w")
        self.sampleSize_Label = ttk.Label(
            self.bandwidthControlFrame,
            name="samplesize_label")
        self.sampleSize_Label.configure(
            anchor="e",
            justify="right",
            style="Heading2b.TLabel",
            text='Sample\nSize',
            width=10)
        self.sampleSize_Label.grid(column=1, padx="5 0", row=0, sticky="e")
        self.calculatedSampleSize_Label = ttk.Label(
            self.bandwidthControlFrame, name="calculatedsamplesize_label")
        self.calculatedSampleSize_VAR = tk.StringVar(value='2000')
        self.calculatedSampleSize_Label.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='2000',
            textvariable=self.calculatedSampleSize_VAR,
            width=8)
        self.calculatedSampleSize_Label.grid(
            column=1, padx="5 0", row=1, sticky="e")
        self.bandwidthControlFrame.pack(anchor="nw", pady="50 0", side="top")
        self.optionFrame.pack(anchor="ne", expand=True, fill="x", side="top")
        self.controlButtonFrame = ttk.Frame(
            self.controlFrame, name="controlbuttonframe")
        self.controlButtonFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.recenter_Button = ttk.Button(
            self.controlButtonFrame, name="recenter_button")
        self.recenter_Button.configure(
            style="Button2b.TButton", text='Recenter', width=10)
        self.recenter_Button.pack(side="top")
        self.recenter_Button.configure(command=self.recenter_CB)
        self.startStop_Button = ttk.Button(
            self.controlButtonFrame, name="startstop_button")
        self.startStopSpectrum_VAR = tk.StringVar(value='Start')
        self.startStop_Button.configure(
            style="Button2b.TButton",
            text='Start',
            textvariable=self.startStopSpectrum_VAR,
            width=10)
        self.startStop_Button.pack(pady="50 0", side="top")
        self.startStop_Button.configure(command=self.startStopSpectrum_CB)
        self.controlButtonFrame.pack(
            anchor="ne",
            expand=True,
            fill="x",
            pady="130 0",
            side="top")
        self.controlFrame.grid(
            column=1,
            padx="10 0",
            row=0,
            rowspan=3,
            sticky="ne")
        self.closingFrame = ttk.Frame(
            self.frequencySpectrum_Labelframe,
            name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.applyClose_Button = ttk.Button(
            self.closingFrame, name="applyclose_button")
        self.closeApply_Button_VAR = tk.StringVar(value='Close')
        self.applyClose_Button.configure(
            style="Button2b.TButton",
            text='Close',
            textvariable=self.closeApply_Button_VAR,
            width=10)
        self.applyClose_Button.grid(column=2, padx="40 0", row=0)
        self.applyClose_Button.configure(command=self.applyClose_CB)
        self.cancel_Button = ttk.Button(
            self.closingFrame, name="cancel_button")
        self.cancel_Button.configure(
            style="Button2b.TButton", text='Cancel', width=10)
        self.cancel_Button.grid(column=3, padx="40 0", row=0)
        self.cancel_Button.configure(command=self.cancel_CB)
        self.closingFrame.grid(column=0, columnspan=2, pady="20 0", row=1)
        self.closingFrame.grid_anchor("center")
        self.frequencySpectrum_Labelframe.pack(
            expand=True, fill="both", side="top")
        self.configure(height=200, width=800)
        self.geometry("750x550")
        self.title("Frequency Spectrum")
        # Layout for 'frequencySpectrum_Window' skipped in custom widget
        # template.

    def frequencyTuning_CB(self, scale_value):
        pass

    def recenter_CB(self):
        pass

    def startStopSpectrum_CB(self):
        pass

    def applyClose_CB(self):
        pass

    def cancel_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = frequencySpectrumUI(root)
    root.mainloop()
