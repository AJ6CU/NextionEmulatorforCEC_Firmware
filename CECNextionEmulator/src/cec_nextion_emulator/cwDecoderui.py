#!/usr/bin/python3
"""
cwDecoder

Manages decoding of CW.

UI source file: cwDecoder.ui
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
class cwDecoderUI(tk.Toplevel):
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

        self.cwDecoder_Labelframe = ttk.Labelframe(
            self, name="cwdecoder_labelframe")
        self.cwDecoder_Labelframe.configure(
            height=200,
            style="Heading2.TLabelframe",
            text='CW Decode',
            width=200)
        # First object created
        on_first_object_cb(self.cwDecoder_Labelframe)

        self.frequencySpectrumLabelframe = ttk.Labelframe(
            self.cwDecoder_Labelframe, name="frequencyspectrumlabelframe")
        self.frequencySpectrumLabelframe.configure(
            height=150,
            style="Heading3.TLabelframe",
            text='Frequency Spectrum\n',
            width=200)
        self.frequencySpectrumFrame = ttk.Frame(
            self.frequencySpectrumLabelframe,
            name="frequencyspectrumframe")
        self.frequencySpectrumFrame.configure(
            height=180, style="Normal.TFrame", width=200)
        frame2 = ttk.Frame(self.frequencySpectrumFrame)
        frame2.configure(height=140, style="Normal.TFrame", width=200)
        self.frequencyPlotFrame = ttk.Frame(frame2, name="frequencyplotframe")
        self.frequencyPlotFrame.configure(
            height=140, style="Normal.TFrame", width=430)
        self.frequencyPlotCanvas = tk.Canvas(
            self.frequencyPlotFrame, name="frequencyplotcanvas")
        self.frequencyPlotCanvas.configure(
            background="blue", height=160, width=430)
        self.frequencyPlotCanvas.pack(expand=True, fill="both", side="top")
        self.frequencyPlotCanvas.bind(
            "<Button-1>", self.enable_Frequency_Spectrum_CB, add="+")
        self.frequencyPlotCanvas.bind(
            "<Configure>", self.resizeCanvas_CB, add="+")
        self.frequencyPlotcwToneScale = tk.Scale(
            self.frequencyPlotFrame, name="frequencyplotcwtonescale")
        self.frequencyPlotcwToneScale_VAR = tk.StringVar()
        self.frequencyPlotcwToneScale.configure(
            from_=0,
            length=435,
            orient="horizontal",
            relief="raised",
            resolution=1,
            showvalue=False,
            sliderlength=50,
            state="normal",
            to=45,
            variable=self.frequencyPlotcwToneScale_VAR,
            width=30)
        self.frequencyPlotcwToneScale.pack(expand=True, fill="x", side="top")
        self.frequencyPlotcwToneScale.configure(
            command=self.frequencyPlotcwToneScale_CB)
        self.frequencyPlotFrame.pack(
            expand=True, fill="x", padx=5, pady=5, side="left")
        self.frequencyPlotParameterFrame = ttk.Frame(
            frame2, name="frequencyplotparameterframe")
        self.frequencyPlotParameterFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.signalLevelLabel = ttk.Label(
            self.frequencyPlotParameterFrame,
            name="signallevellabel")
        self.signalLevelLabel.configure(
            style="Heading2b.TLabel", text='Signal Level')
        self.signalLevelLabel.pack(pady="0 10", side="top")
        frame3 = ttk.Frame(self.frequencyPlotParameterFrame)
        frame3.configure(height=200, style="Normal.TFrame", width=200)
        self.frequencyDecodeScale = tk.Scale(
            frame3, name="frequencydecodescale")
        self.frequencyDecodeScale_VAR = tk.StringVar()
        self.frequencyDecodeScale.configure(
            from_=10,
            length=120,
            orient="vertical",
            relief="raised",
            resolution=1,
            showvalue=False,
            sliderlength=50,
            state="normal",
            to=0,
            variable=self.frequencyDecodeScale_VAR,
            width=30)
        self.frequencyDecodeScale.pack(anchor="n", side="left")
        self.frequencyDecodeScale.configure(
            command=self.frequencyDecodeScale_CB)
        self.frequencyPlotSettingsFrame = ttk.Frame(
            frame3, name="frequencyplotsettingsframe")
        self.frequencyPlotSettingsFrame.configure(
            height=200, style="Normal.TFrame", width=200)
        self.frequencyHighLabel = ttk.Label(
            self.frequencyPlotSettingsFrame,
            name="frequencyhighlabel")
        self.frequencyHighLabel.configure(style="Heading2b.TLabel", text='Max')
        self.frequencyHighLabel.grid(column=0, row=0, sticky="w")
        self.frequencyHighValueLabel = ttk.Label(
            self.frequencyPlotSettingsFrame,
            name="frequencyhighvaluelabel")
        self.frequencyHighValue_VAR = tk.StringVar(value='0')
        self.frequencyHighValueLabel.configure(
            anchor="e",
            justify="right",
            style="Heading2b.TLabel",
            text='0',
            textvariable=self.frequencyHighValue_VAR,
            width=4)
        self.frequencyHighValueLabel.grid(column=1, row=0, sticky="e")
        self.frequencySigLabel = ttk.Label(
            self.frequencyPlotSettingsFrame,
            name="frequencysiglabel")
        self.frequencySigLabel.configure(
            style="Heading2b.TLabel", text='CW\nTHR')
        self.frequencySigLabel.grid(column=0, pady="20 0", row=1, sticky="w")
        self.frequencySigValueLabel = ttk.Label(
            self.frequencyPlotSettingsFrame,
            name="frequencysigvaluelabel")
        self.frequencySigValue_VAR = tk.StringVar(value='20')
        self.frequencySigValueLabel.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='20',
            textvariable=self.frequencySigValue_VAR,
            width=4)
        self.frequencySigValueLabel.grid(
            column=1, pady="20 0", row=1, sticky="e")
        self.frequencyLowLabel = ttk.Label(
            self.frequencyPlotSettingsFrame,
            name="frequencylowlabel")
        self.frequencyLowLabel.configure(style="Heading2b.TLabel", text='Min')
        self.frequencyLowLabel.grid(column=0, pady="20 0", row=2, sticky="w")
        self.frequencyLowValueLabel = ttk.Label(
            self.frequencyPlotSettingsFrame,
            name="frequencylowvaluelabel")
        self.frequencyLowValue_VAR = tk.StringVar(value='0')
        self.frequencyLowValueLabel.configure(
            anchor="e",
            style="Heading2b.TLabel",
            text='0',
            textvariable=self.frequencyLowValue_VAR,
            width=4)
        self.frequencyLowValueLabel.grid(
            column=1, pady="20 0", row=2, sticky="e")
        self.frequencyPlotSettingsFrame.pack(
            anchor="n", expand=True, fill="x", padx="10 0", side="top")
        frame3.pack(expand=True, fill="x", side="top")
        frame1 = ttk.Frame(self.frequencyPlotParameterFrame)
        frame1.configure(height=200, style="Normal.TFrame", width=200)
        self.frequencyPlotcwToneValueLabel = ttk.Label(
            frame1, name="frequencyplotcwtonevaluelabel")
        self.frequencyPlotcwToneValue_VAR = tk.StringVar(value='800')
        self.frequencyPlotcwToneValueLabel.configure(
            style="Heading2b.TLabel",
            text='800',
            textvariable=self.frequencyPlotcwToneValue_VAR)
        self.frequencyPlotcwToneValueLabel.pack(padx=5, side="left")
        self.resetMinMax_Button = ttk.Button(frame1, name="resetminmax_button")
        self.resetMinMax_Button.configure(
            style="Button2b.TButton", text='Reset\nMin/Max', width=12)
        self.resetMinMax_Button.pack(anchor="e", side="right")
        self.resetMinMax_Button.configure(command=self.resetMinMax_CB)
        frame1.pack(expand=True, fill="x", side="left")
        self.frequencyPlotParameterFrame.pack(
            expand=True, fill="both", padx="5 0", side="top")
        frame2.pack(expand=True, fill="x", padx=10, side="top")
        self.frequencySpectrumFrame.pack(expand=True, fill="x", side="top")
        self.frequencySpectrumLabelframe.pack(
            expand=True, fill="x", padx=5, side="top")
        self.cwDecodeLabelframe = ttk.Labelframe(
            self.cwDecoder_Labelframe, name="cwdecodelabelframe")
        self.cwDecodeLabelframe.configure(
            height=150,
            style="Heading3.TLabelframe",
            text='CW Decode',
            width=200)
        self.cwDecodeFrame = ttk.Frame(
            self.cwDecodeLabelframe, name="cwdecodeframe")
        self.cwDecodeFrame.configure(
            height=100, style="Normal.TFrame", width=200)
        self.cwDecodedText = tk.Text(self.cwDecodeFrame, name="cwdecodedtext")
        self.cwDecodedText.configure(
            background="blue",
            font="{Arial} 18 {}",
            foreground="lightgray",
            height=3,
            spacing1=2,
            spacing2=5,
            spacing3=2,
            state="normal",
            width=50,
            wrap="char")
        self.cwDecodedText.pack(
            expand=True,
            fill="x",
            padx=5,
            pady=5,
            side="top")
        self.cwDecodedText.bind(
            "<Button-1>",
            self.enable_CW_Decode_CB,
            add="+")
        self.cwDecodeFrame.pack(expand=True, fill="x", side="top")
        self.cwDecodeLabelframe.pack(expand=True, fill="x", padx=5, side="top")
        self.closingFrame = ttk.Frame(
            self.cwDecoder_Labelframe,
            name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.close_Button = ttk.Button(self.closingFrame, name="close_button")
        self.close_Button.configure(
            style="Button2b.TButton", text='Close', width=10)
        self.close_Button.grid(column=3, padx="10 0", row=0)
        self.close_Button.configure(command=self.close_CB)
        self.closingFrame.pack(expand=True, fill="x")
        self.closingFrame.grid_anchor("center")
        self.cwDecoder_Labelframe.pack(expand=True, fill="both", side="top")
        self.configure(height=200, width=800)
        self.geometry("600x430")
        self.title("CW Decode")
        # Layout for 'cwDecoder_Window' skipped in custom widget template.

    def enable_Frequency_Spectrum_CB(self, event=None):
        pass

    def resizeCanvas_CB(self, event=None):
        pass

    def frequencyPlotcwToneScale_CB(self, scale_value):
        pass

    def frequencyDecodeScale_CB(self, scale_value):
        pass

    def resetMinMax_CB(self):
        pass

    def enable_CW_Decode_CB(self, event=None):
        pass

    def close_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = cwDecoderUI(root)
    root.mainloop()
