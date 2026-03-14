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
            translator = i18n_translator_noop
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = image_loader_default
        if on_first_object_cb is None:
            on_first_object_cb = first_object_callback_noop

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

        frame1 = ttk.Frame(self.cwDecoder_Labelframe)
        frame1.configure(height=200, style="Normal.TFrame", width=200)
        self.frequencySpectrumLabelframe = ttk.Labelframe(
            frame1, name="frequencyspectrumlabelframe")
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
        self.frequencySpectrumFrame.pack(expand=True, fill="x", side="top")
        self.test_button = ttk.Button(
            self.frequencySpectrumLabelframe,
            name="test_button")
        self.test_button.configure(text='button1')
        self.test_button.pack(side="top")
        self.test_button.configure(command=self.testButton_cb)
        self.frequencySpectrumLabelframe.pack(
            expand=True, fill="x", padx=5, side="top")
        self.cwDecodeLabelframe = ttk.Labelframe(
            frame1, name="cwdecodelabelframe")
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
            font="{Arial} 18 {}",
            height=3,
            spacing1=2,
            spacing2=5,
            spacing3=2,
            state="disabled",
            width=50,
            wrap="char")
        _text_ = '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678'
        self.cwDecodedText.configure(state="normal")
        self.cwDecodedText.insert("0.0", _text_)
        self.cwDecodedText.configure(state="disabled")
        self.cwDecodedText.pack(padx=5, pady=5, side="top")
        self.cwDecodeFrame.pack(expand=True, fill="x", side="top")
        self.cwDecodeLabelframe.pack(expand=True, fill="x", padx=5, side="top")
        self.closingFrame = ttk.Frame(frame1, name="closingframe")
        self.closingFrame.configure(style="Normal.TFrame")
        self.decodeToggle_Button = ttk.Button(
            self.closingFrame, name="decodetoggle_button")
        self.decodeToggle_Button.configure(
            style="Button2b.TButton", text='Start Decode', width=14)
        self.decodeToggle_Button.grid(column=0, row=0)
        self.decodeToggle_Button.configure(command=self.decodeToggle_CB)
        self.close_Button = ttk.Button(self.closingFrame, name="close_button")
        self.close_Button.configure(style="Button2b.TButton", text='Close')
        self.close_Button.grid(column=3, padx="10 0", row=0)
        self.close_Button.configure(command=self.close_cwDecode_Window_CB)
        self.closingFrame.pack(expand=True, fill="x")
        self.closingFrame.grid_anchor("center")
        frame1.pack(expand=True, fill="both", side="top")
        self.cwDecoder_Labelframe.pack(expand=True, fill="both", side="top")
        self.configure(height=200, width=800)
        self.geometry("600x430")
        self.title("CW Decode")
        # Layout for 'cwDecoder_Window' skipped in custom widget template.

    def testButton_cb(self):
        pass

    def decodeToggle_CB(self):
        pass

    def close_cwDecode_Window_CB(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = cwDecoderUI(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
