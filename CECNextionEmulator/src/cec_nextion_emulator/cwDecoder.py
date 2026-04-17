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
        #   Flags
        #

        #   This is a tristate flag that determines the state of the UX
        #   Can only do Frequency/Spectrum or CW decode (or nothing)
        self.spectrumMorseState = None  # None = not initialized,
                                        # "FreqScan" = Frequency/Spectrum Mode
                                        # "CWDecode" = CW Decode Mode


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

        gv.trimAndLocateWindow(self.master, 0, 0)

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

        self.enable_Frequency_Spectrum()                # Start with the frequency scan

        #
        #   Request existing saved data in EEPROM
        #
        self.request_DSP_EEPROM_Data()


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
        #
        #   Executed when Button-1 clicked on Frequency/Spectrum Frame (or children)
        #
        self.unbind_all("<Button-1>")

        self.spectrumMorseState = "FreqScan"      # Set state flag Frequency/Spectrum mode

        self.setcwDecodeState("disabled")
        self.setFrequencySpectrumState("normal")

    def enable_CW_Decode(self, event=None):
        #
        #   Executed when Button-1 clicked on CW_Decode Frame (or children)
        #
        self.unbind_all("<Button-1>")

        self.spectrumMorseState = "CWDecode"      # Set state flag to True = CW Decode Mode mode

        self.setcwDecodeState("normal")
        self.setFrequencySpectrumState("disabled")

    def setcwDecodeState(self, newState):
        if newState == "normal":
            self.cwDecodedText.configure(foreground="black")
        else:
            self.cwDecodedText.configure(foreground="lightgray")


    def setFrequencySpectrumState(self, newState):
        self.frequencyPlotcwToneValueLabel.configure(state=newState)

        self.frequencyHighLabel.configure(state=newState)
        self.frequencySigLabel.configure(state=newState)
        self.frequencyLowLabel.configure(state=newState)

        self.frequencyHighValueLabel.configure(state=newState)
        self.frequencySigValueLabel.configure(state=newState)
        self.frequencyLowValueLabel.configure(state=newState)

    #
    #   EEPROM Variable load functions
    #
    def request_DSP_EEPROM_Data(self):
        #
        # Temp comment out
        #
        # self.mainWindow.theRadio.RequestDSP_EEPROM_Data()
        #
        # following just plugs to allow basic testing
        #
        self.mainWindow.UseDSP = True
        self.spectrumMorseState = "FreqScan"

    def process_DSP_EEPROM_Data(self, buffer):
        byteList = int(buffer).tobytes(3,'little')

        self.frequencyDecodeScale_VAR.set(byteList[0]/10)

        if byteList[1] == 1:
            self.mainWindow.UseDSP =  True
        else:
            self.mainWindow.UseDSP = False

        if byteList[2] == 95:       # This is the code for being in spectrum mode
            self.spectrumMorseState = "FreqScan"      # Set state flag Frequency/Spectrum mode

        #
        #   in CWDecode mode, this byte is between 100 and < 146. The offset from 100
        #   is the offset (*50 +300) within the SSB bandwidth. So the scan is limited to be
        #   between 300(scale=0) and (50*45 + 300 = 2550)
        #   So a very little room to scan the band, really just fine tuning within a frequency
        #
        elif ((byteList[2] >= 100) and (byteList[2] < 146)):
            self.spectrumMorseState = "CWDecode"
            self.frequencyPlotcwToneScale_VAR.set(str(byteList[2]-100))
            self.frequencyPlotcwToneValue_VAR.set(
                str((int(self.frequencyPlotcwToneScale_VAR.get())*50)+300))   # 10*50 + 300

    #
    #   Data processors
    #
    def process_Spectrum_Data(self, buffer):

        centerFreq = int(self.frequencyPlotcwToneValue_VAR.get()) / 50
        vSelectMin = centerFreq
        vSelectMax = centerFreq + 2
        centerFreqTop = (centerFreq+1) * 4

        # the variables below size the bar graph
        # experiment with them to fit your needs
        # highest y = max_data_value * y_stretch
        y_stretch = 2
        # gap between lower canvas edge and x axis
        y_gap = -15
        # stretch enough to get all data items in
        x_stretch = 6
        x_width = 4
        # gap between left canvas edge and y axis
        x_gap = 5
        c_height =150


        byteBuffer = bytearray.fromhex(buffer)          #This gives us an array of hex bytes

        for x, y in enumerate(byteBuffer):
            ymag = y>>1
            if ymag < 0:
                ymag = 0
            else:
                if (ymag > 70):
                    ymag = 70

            # calculate reactangle coordinates (integers) for each bar
            x0 = x * x_stretch + x * x_width + x_gap
            y0 = c_height - (ymag * y_stretch + y_gap)
            x1 = x * x_stretch + x * x_width + x_width + x_gap
            y1 = c_height - y_gap
            # draw the bar
            self.frequencyPlotCanvas.create_rectangle(x0, y0, x1, y1, fill="lightgray", outline="lightgray")

            if x > vSelectMin:
                if x < vSelectMax:
                    self.frequencyPlotCanvas.create_line(x0, y0, x1, y1, fill='red')
                    self.frequencyPlotCanvas.create_line(x0+4, y0, x1+4, y1, fill='red')




    def process_CWDecoded_Data(self, buffer):
        for char in buffer:
            self.logCW_Character(char)

    #
    #   Get/Setters
    #

    def get_spectrumMorseState(self):
        return self.spectrumMorseState

    def set_spectrumMorseState(self, newState):
        self.spectrumMorseState = newState


    def frequencyDecodeScale_CB(self, scale_value):
        self.frequencySigValue_VAR.set(str(int(self.frequencyDecodeScale_VAR.get())*10))  # 2*10

    def frequencyPlotcwToneScale_CB(self, scale_value):
        self.frequencyPlotcwToneValue_VAR.set(str(((int(self.frequencyPlotcwToneScale_VAR.get())*50)+300)))

    def startStopToggleButton_CB(self):
        self.logCW_Character("S")


    def close_CB(self):
        self.spectrumMorseState = None
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
