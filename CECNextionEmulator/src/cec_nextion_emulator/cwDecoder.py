#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import cwDecoderui as baseui
from barPlotter import barPlotter
from cwLogger import cwLogger
import globalvars as gv
from tkinter import messagebox


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

        self.windowResized = False      # these two variables are used to handle resizing of screen
        self.windowResizedObj = None    # while window is active. When the resized is detected,
                                        # the windowResized flag is set to true and a future
                                        # event is created to eventually update the window after 100ms
                                        # Each time the reseize event is called, the current future event
                                        # is deleted and a new one is scheduled. Only after 100 ms of no
                                        # new resize, is the scheduled event finally executed, the graph is
                                        # updated and the flag is set back to False.

        self.initUX()

    def initUX(self):
        self.title("CW Decode")
        self.geometry("600x430")
        self.minsize(600,430)
        self.wait_visibility()  # required on Linux
        self.grab_set()
        self.transient(self.master)

        gv.trimAndLocateWindow(self.master, 0, 0)


        #
        #   get defaults from mainwindow
        #

        self.frequencyDecodeScale_VAR.set(str(self.mainWindow.frequencyDecodeScale))
        self.frequencySigValue_VAR.set(str(self.mainWindow.frequencyDecodeScale*10))            # 2*10

        self.frequencyPlotcwToneScale_VAR.set(self.mainWindow.frequencyPlotcwToneScale)
        self.frequencyPlotcwToneValue_VAR.set(str(self.mainWindow.frequencyPlotcwToneValue))

        self.frequencyHighValue_VAR.set('0')        # Reset min/max on entry
        self.frequencyLowValue_VAR.set(self.frequencySigValue_VAR.get())

        self.FFTSIZE = 63   # Maximum number of times that the ADC can be read.
                            # Appears to be a bug in the DSP code. Suppose to be 64 elements (0-63) but only
                            # really sends 0-62
                                # Machine dependent. About

        self.FREQ_Y_MAX = 70  # maximum value of Y values
        #
        #   Create plotter object and bind it to the frequencyPlotCanvas of this window
        #
        self.plotter = barPlotter(self, self.frequencyPlotCanvas, self.FFTSIZE, self.FREQ_Y_MAX)
        self.logger = cwLogger(self, self.cwDecodedText, 150)
        if  self.mainWindow.frequencySpectrumMode == "FreqScan":
            self.enable_Frequency_Spectrum_CB()  # Start with the frequency scan
        else:
            self.enable_CW_Decode_CB()



    def enable_Frequency_Spectrum_CB(self, event=None):
        #
        #   Executed when Button-1 clicked on Frequency/Spectrum Frame (or children)
        #

        self.spectrumMorseState = "FreqScan"      # Set state flag Frequency/Spectrum mode

        self.setcwDecodeState("disabled")
        self.setFrequencySpectrumState("normal")
        self.mainWindow.theRadio.Set_Spectrum_Mode(95)  # Magic number indicating it is a spectrum scan
        self.resetMinMax_CB()   # reset min/max signals to zero

    def enable_CW_Decode_CB(self, event=None):
        #
        #   Executed when Button-1 clicked on CW_Decode Frame (or children)
        #

        self.spectrumMorseState = "CWDecode"      # Set state flag to True = CW Decode Mode mode

        self.setcwDecodeState("normal")
        self.setFrequencySpectrumState("disabled")
        value = int(self.frequencyPlotcwToneValue_VAR.get()) - 300

        # following code is just to encode the tone setting and the fact that it is a CW
        value = value // 50

        value = value + 100     # this maps the final byte to between 100-129
                                # which means decode morse

        self.mainWindow.theRadio.Set_Spectrum_Mode(value)

    def setcwDecodeState(self, newState):
        if newState == "normal":
            self.cwDecodedText.configure(background="blue")
        else:
            self.cwDecodedText.configure(background="gray")



    def setFrequencySpectrumState(self, newState):
        if newState == "normal":
            self.frequencyPlotFrame.state(['!disabled'])
            self.resetMinMax_Button.state(['!disabled'])
            self.frequencyPlotCanvas.configure(bg="blue")

        else:
            self.frequencyPlotFrame.state(['disabled'])
            self.resetMinMax_Button.state(['disabled'])
            self.frequencyPlotCanvas.configure(bg="gray")

    #
    #   EEPROM Variable load functions
    #
    def request_DSP_EEPROM_Data(self):
        #
        # Request DSP data stored in EEPROM
        self.mainWindow.theRadio.Req_DSP_EEPROM_Settings()


    # def process_DSP_EEPROM_Data(self, buffer):
    #     byteList = int(buffer).to_bytes(4,'little')
    #     # print("process_DSP_Data", byteList)
    #
    #     if int(buffer) < 0xffffff:          # only a 3 hex byte number
    #
    #         print("eeprom values returned")
    #         print("decodescale*10=", byteList[0])
    #         print("useDSPFlag=", byteList[1])
    #
    #         self.frequencyDecodeScale_VAR.set(byteList[0]/10)
    #         self.frequencySigValue_VAR.set(byteList[0])
    #
    #         if byteList[1] == 1:
    #             self.mainWindow.UseDSP =  "True"
    #         else:
    #             self.mainWindow.UseDSP = "False"

    #
    #   Data processors
    #
    def process_Spectrum_Data(self, buffer):
        # print("buffer size=", len(buffer))
        self.plotter.process_Data(buffer)
        self.frequencyLowValue_VAR.set(str( self.plotter.get_CurrentMin()))
        self.frequencyHighValue_VAR.set(str( self.plotter.get_CurrentMax()))
        self.updateTargetFreqBars()
    #
    #   Update bars attached to a scroll bar that helps identify target frequency
    #

    def updateTargetFreqBars(self):
        #   get the length of the scale and add 1 ("fence post rule")
        scaleLength = int(self.frequencyPlotcwToneScale["to"] - self.frequencyPlotcwToneScale["from"]) + 1
        #
        #   this calculation maps the scale (0-45) until the FFT Size (0-63)
        #   this allows us to draw two vertical lines that help target the apparent CW signal in the range
        #
        barPos = round((int(self.frequencyPlotcwToneScale_VAR.get()) / scaleLength) * self.FFTSIZE)
        self.plotter.drawHighLightBars(barPos)

    #
    #   Display CW in the target text box.
    #   logCW does the work of managing the text box and rolling characters off display (FIFO)
    #
    def process_CWDecoded_Data(self, buffer):
        print("Processing CW Decoded in window", buffer)
        self.logger.process_CWDecoded_Data(buffer)

    #
    #   Callbacks
    #

    def frequencyDecodeScale_CB(self, scale_value):
        # print("scale_value:", scale_value, type(scale_value))
        self.frequencySigValue_VAR.set(str(int(scale_value)*10))
        self.mainWindow.theRadio.Set_Signal_Value(scale_value)

    def frequencyPlotcwToneScale_CB(self, scale_value):
        self.frequencyPlotcwToneValue_VAR.set(str(((int(scale_value)*50)+300)))
        self.updateTargetFreqBars()

    def resetMinMax_CB(self):
        self.plotter.set_CurrentMax(0)
        self.plotter.set_CurrentMin(0)



    def close_CB(self):
        self.mainWindow.frequencySpectrumMode =  self.spectrumMorseState
        self.spectrumMorseState = None
        self.mainWindow.consumerDSPdata = self.mainWindow
        self.mainWindow.highlightCWorSpectrumBoxes(True)
        self.destroy()





        #
        #   resizeCanvas_CB and refreshCanvas work together to de2al with any resizing of the canvas.
        #   When a resize is detected, resizeCanvas_CB is called and it schedules a future execution of
        #   refreshCanvas.  But resizing generates a lot of callbacks... So if the resize process is underway
        #   each new event cancels the prior "after refreshCanvas" and creates a new one 100ms in the future
        #   Eventually the events end, and the last refreshCanvas future event runs and replots the data
        #

    def resizeCanvas_CB(self, event=None):
        if self.windowResized:
            self.master.after_cancel(self.windowResizedObj)
        else:
            self.windowResized = True
        self.windowResizedObj = self.master.after(100, self.refreshCanvas)

    def refreshCanvas(self):

        #
        #   Update canvas size
        #
        self.plotter.refreshCanvas()
        self.updateTargetFreqBars()


