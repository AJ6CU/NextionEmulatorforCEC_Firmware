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


        #
        #   set defaults for scale
        #
        self.frequencyPlotcwToneScale_VAR.set("10")
        self.frequencyPlotcwToneValue_VAR.set("800")    # 10*50 + 300

        self.frequencyDecodeScale_VAR.set("2")
        self.frequencySigValue_VAR.set("20")            # 2*10

        self.enable_Frequency_Spectrum_CB()                # Start with the frequency scan

        #
        #   Request existing saved data in EEPROM
        #
        self.request_DSP_EEPROM_Data()



    def enable_Frequency_Spectrum_CB(self, event=None):
        #
        #   Executed when Button-1 clicked on Frequency/Spectrum Frame (or children)
        #

        self.spectrumMorseState = "FreqScan"      # Set state flag Frequency/Spectrum mode

        self.setcwDecodeState("disabled")
        self.setFrequencySpectrumState("normal")
        self.startStopToggleButton_VAR.set("Run Spectrum")

    def enable_CW_Decode_CB(self, event=None):
        #
        #   Executed when Button-1 clicked on CW_Decode Frame (or children)
        #

        self.spectrumMorseState = "CWDecode"      # Set state flag to True = CW Decode Mode mode

        self.setcwDecodeState("normal")
        self.setFrequencySpectrumState("disabled")

        self.startStopToggleButton_VAR.set("Run CW Decode")

    def setcwDecodeState(self, newState):
        if newState == "normal":
            self.cwDecodedText.configure(foreground="white")
        else:
            self.cwDecodedText.configure(foreground="gray")


    def setFrequencySpectrumState(self, newState):
        if newState == "normal":
            self.frequencyPlotFrame.state(['!disabled'])
        else:
            self.frequencyPlotFrame.state(['disabled'])
    #     self.frequencyPlotcwToneValueLabel.configure(state=newState)
    #
    #     self.frequencyHighLabel.configure(state=newState)
    #     self.frequencySigLabel.configure(state=newState)
    #     self.frequencyLowLabel.configure(state=newState)
    #
    #     self.frequencyHighValueLabel.configure(state=newState)
    #     self.frequencySigValueLabel.configure(state=newState)
    #     self.frequencyLowValueLabel.configure(state=newState)

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
        match self.startStopToggleButton_VAR.get():
            case "Run Spectrum":
                self.startStopToggleButton_VAR.set("Stop Spectrum")
            case "Stop Spectrum":
                self.startStopToggleButton_VAR.set("Run Spectrum")
            case "Run CW Decode":
                self.startStopToggleButton_VAR.set("Stop CW Decode")
            case "Stop CW Decode":
                self.startStopToggleButton_VAR.set("Run CW Decode")
            case _:
                print("unknown toggle button state=", self.startStopToggleButton_VAR.get())

    def close_CB(self):
        self.spectrumMorseState = None
        self.mainWindow.consumerDSPdata = self.mainWindow
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
