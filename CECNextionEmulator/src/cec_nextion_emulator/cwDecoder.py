#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import cwDecoderui as baseui
import globalvars as gv


#
# Manual user code
#

class cwDecoder(baseui.cwDecoderUI):
    def __init__(self,  master=None, mainWindow=None, **kw):
        self.master = master
        self.mainWindow = mainWindow
        #
        #   Create a toplevel window to contain the settings master
        #
        # self.master = tk.Toplevel(self.master)

        super().__init__(self.master, **kw)
        #
        #   Make sure that a close by the Window manager goes to the same close callback
        #
        self.protocol("WM_DELETE_WINDOW", self.close_CB)

        self.initUX()

    def initUX(self):
        self.title("CW Decode")
        self.geometry("600x430")
        self.wait_visibility()  # required on Linux
        self.grab_set()
        self.transient(self.master)

        # self.pack(expand=tk.YES, fill=tk.BOTH)
        # gv.trimAndLocateWindow(self.master, 0, 0)

        self.cwDecodeLabelframe.bind("<Enter>", self.bind_all("<Button-1>", self.cwDecode_bind_all))
        self.frequencySpectrumFrame.bind("<Enter>", self.bind_all("<Button-1>", self.frequency_bind_all))

        self.closingFrame.bind("<Enter>", self.close_frame_unbind_all)
        #
        #   set defaults for scale
        #
        self.frequencyPlotcwToneScale_VAR.set("10")
        self.frequencyPlotcwToneValue_VAR.set("800")    # 10*50 + 300

        self.frequencyDecodeScale_VAR.set("2")
        self.frequencySigValue_VAR.set("20")            # 2*10

    #
    #   The following two "bind_all' functions ensures that any mouse clicks, regardless of which
    #   widget is clicked, results in a call to the enable either Spectrum(Frequency) or CW windows
    #   This eliminates the needs for a radio button to select which mode the data is interpreted as
    #   The Third function (unbind_all) ensures that clicks are not used to select between these two
    #   modes when the pointer is moved outside the Spectrum/CW windows.
    #

    def frequency_bind_all(self):
        # print("binding frequency spectrum")
        #
        # Deliver a Button-1 click to a function to enable Frequency/Spectrum
        #
        self.bind_all("<Button-1>", self.enable_Frequency_Spectrum)

    def cwDecode_bind_all(self):
        # self.unbind_all("<Button-1>")
        # print("binding cw decoding spectrum")
        #
        # Deliver a Button-1 click to a function to enable CW processing
        #
        self.bind_all("<Button-1>", self.enable_CW_Decode)

    def close_frame_unbind_all(self, event=None):
        # print("unbinding frame")
        #
        #   Moved away from the Spectrum(Frequency) and CW frames, so unbind any clicks
        self.unbind_all("<Button-1>")


    def enable_Frequency_Spectrum(self, event=None):
        # print("frequency spectrum clicked")
        self.unbind_all("<Button-1>")
        self.cwDecodedText.configure(foreground="lightgray")

        self.frequencyPlotcwToneValueLabel.configure(state="normal")
        self.frequencyHighLabel.configure(state="normal")
        self.frequencySigLabel.configure(state="normal")
        self.frequencyLowLabel.configure(state="normal")

        self.frequencyHighValueLabel.configure(state="normal")
        self.frequencySigValueLabel.configure(state="normal")
        self.frequencyLowValueLabel.configure(state="normal")

    def enable_CW_Decode(self, event=None):
        # print("cw decode clicked")
        self.unbind_all("<Button-1>")
        self.cwDecodedText.configure(foreground="black")
        self.frequencyPlotcwToneValueLabel.configure(state="disabled")

        self.frequencyHighLabel.configure(state="disabled")
        self.frequencySigLabel.configure(state="disabled")
        self.frequencyLowLabel.configure(state="disabled")

        self.frequencyHighValueLabel.configure(state="disabled")
        self.frequencySigValueLabel.configure(state="disabled")
        self.frequencyLowValueLabel.configure(state="disabled")





    def frequencyDecodeScale_CB(self, scale_value):
        self.frequencySigValue_VAR.set(str(int(self.frequencyDecodeScale_VAR.get())*10))  # 2*10

    def frequencyPlotcwToneScale_CB(self, scale_value):
        self.frequencyPlotcwToneValue_VAR.set(str(((int(self.frequencyPlotcwToneScale_VAR.get())*50)+300)))

    def startStopToggleButton_CB(self):
        self.logCW_Character("S")


    def close_CB(self):
        print("close_cwDecode_Window_CB")
        self.unbind_all("<Button-1>")   # Eliminate global catch of Button-1
        self.destroy()

    def logCW_Character (self,newchar):
        if len(self.cwDecodedText.get('1.0', 'end')) > 130:   # Not maximum, but close to it
            self.cwDecodedText.delete('1.0')
        self.cwDecodedText.insert('2.end',newchar)

myroot=None
mainWindow=None


def launch_widget():
    widget= cwDecoder(myroot,mainWindow)

if __name__ == "__main__":
    myroot = tk.Tk()

    Launch_Button = ttk.Button(myroot, text="Launch")
    Launch_Button.configure(text='Launch')
    Launch_Button.configure(command=cwDecoder)
    Launch_Button.pack(side="top")

    myroot.mainloop()
