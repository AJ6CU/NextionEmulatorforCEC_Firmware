#!/usr/bin/python3
"""
Frequency Spectrum

Displays an area of the Frequency showing signal strength

UI source file: frequencySpectrum.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from unittest import case

import frequencySpectrumui as baseui
import random
from time import sleep

import mystyles
from barPlotter import barPlotter
import globalvars as gv


#
# Manual user code
#

class frequencySpectrum(baseui.frequencySpectrumUI):
    def __init__(self,  master=None, mainWindow=None, centerFrequency=None, **kw):
        self.master = master
        self.mainWindow = mainWindow
        self.centerFrequency = centerFrequency          # the current (VFO) frequency is passed and saved
        self.originalFrequency = centerFrequency        # Save frequency at entry so can restore if cancel

        self.startFrequency = None                      # starting frequency for scanning
        self.stopFrequency = None                       # stopping frequency for scanning
        self.bandwidth = None                           # the width of the band being scanned
        self.stepSize = None                            # size of steps (frequency samples)
        self.lastCenterFrequency = None                 # tracks the last center frequency in case it has been changed
                                                        # between scans
        self.tuningLine = None                          # used to save the tuning line object

        self.frequencyScrolling = False                 # tracks when the scrollbar is being used to adjust frequency

        #
        #   DEFAULTS
        #

        self.lastCenterFrequency = self.centerFrequency     # save current frequency, need this to check if current
                                                            # frequency has been changed

        self.MaxADCCount = 120  # Maximum number of times that the ADC can be read.
                                # Machine dependent. About

        # self.FREQ_X_GAP = 4  # gap between left canvas edge and y axis
        # self.FREQ_Y_GAP = 0  # gap between lower canvas edge and x axis
        self.FREQ_Y_MAX = 70  # maximum value of Y values

        # self.frequencyLineObj = [None] * self.MaxADCCount * 1
        # self.frequencyLineYmag = [None] * self.MaxADCCount * 1
        # self.frequencyLineX0 = [None] * self.MaxADCCount * 1
        # self.frequencyLineX1 = [None] * self.MaxADCCount * 1
        self.peakBuffer = bytearray(self.MaxADCCount)       # Tracks the peak value of a frequency
        self.averageBuffer = bytearray(self.MaxADCCount)    # Tracks the current average of a frequency



        self.spectrumScanning = False               # default to scanning off

        self.windowResized = False                  # these two variables are used to handle resizing of screen
        self.windowResizedObj = None                # while window is active. When the resized is detected,
                                                    # the windowResized flag is set to true and a future
                                                    # event is created to eventually update the window after 100ms
                                                    # Each time the reseize event is called, the current future event
                                                    # is deleted and a new one is scheduled. Only after 100 ms of no
                                                    # new resize, is the scheduled event finally executed, the graph is
                                                    # updated and the flag is set back to False.
        self.frequencyChangeCheckPtr = None         # used to track the routine that checks for frequency changes from the knob

        self.initUXComplete = False

        super().__init__(self.master, **kw)


        #
        #   Make sure that a close by the Window manager goes to the same close callback
        #
        self.protocol("WM_DELETE_WINDOW", self.cancel_CB)

        self.initUX()           # This deals with any initiation that needs to be done after the Object is fully
                                # instantiated.

    def initUX(self):
        # self.title("Frequency Spectrum")
        self.geometry("800x650")

        self.wait_visibility()  # required on Linux
        self.grab_set()
        self.transient(self.master)

        # gv.trimAndLocateWindow(self.master, 0, 0)     # causes annoying resizing on initialization of window

        gv.formatCombobox(self.repeat_Combobox, "Arial", "24", "bold")
        gv.formatCombobox(self.bandwidth_Combobox, "Arial", "24", "bold")

        gv.formatCombobox(self.minSignal_Combobox, "Arial", "24", "bold")
        gv.formatCombobox(self.maxSignal_Combobox, "Arial", "24", "bold")


        # Update bandwidth to use selected delimiter

        if gv.NUMBER_DELIMITER != '':                   # temporary to handle standalone testing
            localizedBandwidth=[]
            for item in self.bandwidth_Combobox['values']:
                localizedBandwidth.append(item.replace(',', gv.NUMBER_DELIMITER))
            self.bandwidth_Combobox['values']=localizedBandwidth


        self.repeat_VAR.set('10')
        self.bandwidthSelected_VAR.set('240,000')
        self.minSignal_VAR.set('0')
        self.maxSignal_VAR.set('255')

        # print("before call to updatescanparameters",self.bandwidthSelected_VAR.get(),self.bandwidthSelected_VAR.get().replace(",","").replace(".",""))


        self.updateScanParameters()     # Can now format Frequency graphs

        self.frequencyTuning_VAR.set(60)                               # Set scrollbar in middle
        self.currentFrequency_VAR.set(str(self.lastCenterFrequency))    # Set frequency

        self.plotterAvg = barPlotter(self, self.frequencyPlotCanvas, self.MaxADCCount, self.FREQ_Y_MAX)
        # self.plotterPeak = barPlotter(self, self.frequencyPlotCanvas, self.MaxADCCount, self.FREQ_Y_MAX, barColor="red")
        self.plotterPeak = barPlotter(self, self.waterfall_Canvas, self.MaxADCCount, self.FREQ_Y_MAX, barColor="red")

        self.repeatValueChanged_CB()
        self.checkForFrequencyChange()

        self.initUXComplete = True

    def reinitializeValues(self):
        self.peakBuffer = bytearray(self.MaxADCCount)
        self.averageBuffer = bytearray(self.MaxADCCount)

    def updateScanParameters(self):
        #
        #   When the bandwidth is changed, this routine is called to re-establish the scanning
        #   TODO check if scan running, stop it, reset stuff, and then rerun
        #
        # print(self.bandwidthSelected_VAR.get(),self.bandwidthSelected_VAR.get().replace(",","").replace(".",""))
        self.bandwidth = int(self.bandwidthSelected_VAR.get().replace(",","").replace(".",""))
        self.calculatedSampleSize_VAR.set(int(self.bandwidth / self.MaxADCCount) )

        self.startFrequency=self.roundToNearest((self.centerFrequency - self.bandwidth/2),int(self.calculatedSampleSize_VAR.get()))
        self.startFrequency_VAR.set(str(self.startFrequency))

        self.stopFrequency = self.roundToNearest((self.centerFrequency - int(self.calculatedSampleSize_VAR.get()) + self.bandwidth/2),int(self.calculatedSampleSize_VAR.get()))
        self.stopFrequency_VAR.set(str(self.stopFrequency))

        self.mainWindow.theRadio.updateFrequencySpectrumOptions(int(self.repeat_VAR.get()), 0, self.MaxADCCount, round(int(self.calculatedSampleSize_VAR.get())/20))

        # print("finished updating scan parameters", round(int(self.calculatedSampleSize_VAR.get())/20))


    def updatePeak(self,buffer):
        byteBuffer =bytearray.fromhex(buffer)
        for x, y in enumerate(byteBuffer):
            if y > self.peakBuffer[x]:
                self.peakBuffer[x] = y


    def updateAverage(self,buffer):
        byteBuffer =bytearray.fromhex(buffer)
        valueCount = 1+int(self.repeat_VAR.get()) - int(self.remainingCount_VAR.get())

        for x, y in enumerate(byteBuffer):

            tmp = int(round(self.averageBuffer[x] +((y-self.averageBuffer[x])/valueCount)))

            if tmp > 255:
                print("tmp too big, tmp")
            self.averageBuffer[x] = tmp


    def process_Spectrum_Data(self, buffer):
        #
        # This plots the frequency ADC values. Uses generic routines to figure out sizes of canvas and bar sizes
        #

        self.updateAverage(buffer)          # Process buffer to update the Average of each bar

        self.updatePeak(buffer)             # Process buffer to look for a higher peak


        self.remainingCount_VAR.set(str(int(self.remainingCount_VAR.get()) - 1))        # reduce the count remaining


        if int(self.remainingCount_VAR.get())==0:               #   if zero remaining, then we can plot average and peak

            self.plotterPeak.process_Data(self.peakBuffer)
            self.plotterAvg.process_Data(self.averageBuffer)

            # for i in range(self.MaxADCCount):
            #     if self.averageBuffer[i] > self.peakBuffer[i]:
            #         print("Average exceeds peak, position=", i, "average=", self.averageBuffer[i], "peak=", self.peakBuffer[i])
            #     else:
            #         print("Peak exceeds average, position=", i, "average=", self.averageBuffer[i], " peak=", self.peakBuffer[i])
            # for x in range(self.MaxADCCount):
            #     print("x=", x, self.peakBuffer[x])
            self.updateTuningLine()
            self.scanningComplete()

    def calculateBarPosition(self):
        #
        #   get the length of the scale and add 1 ("fence post rule")
        #   return weighted position on scale
        #
        # scaleLength = int(self.frequencyTuning_Scale["to"] - self.frequencyTuning_Scale["from"]) + 1
        #
        # return(round((float(self.frequencyTuning_VAR.get()) / scaleLength) * (self.MaxADCCount-1)))
        return(int(self.frequencyTuning_VAR.get()))



    def updateTuningLine(self):
        #
        #   Updates the location of the tuning bars
        #
        barPos = self.calculateBarPosition()
        self.plotterAvg.drawHighLightBars(barPos)
        self.plotterPeak.drawHighLightBars(barPos)

    def roundToNearest(self,n,base):
        return base * round(n/base)


    def updateCurrentFrequency(self):
        #
        #   updates the current frequency of the tuning bar as displayed in the middle below the scroll bar
        #
        barPos = self.calculateBarPosition()
        # print("barPos=", barPos)
        # print("updateCurrentFrequency, position=", barPos)
        # self.currentFrequency = int((self.bandwidth * (int(self.frequencyTuning_VAR.get())/scrollBarSpan))+self.startFrequency)
        # roundedToSampleSize = self.roundToNearest((self.bandwidth/(self.MaxADCCount-1)) * barPos, int(self.calculatedSampleSize_VAR.get()))
        # roundedToSampleSize = self.roundToNearest(self.currentFrequency_VAR.get(),int(self.calculatedSampleSize_VAR.get()))*barPos
        self.centerFrequency =  self.startFrequency + (int(self.calculatedSampleSize_VAR.get())*barPos)

        # print("currentFrequency=", self.centerFrequency)
        self.currentFrequency_VAR.set(str(self.centerFrequency))

    def frequencyTuning_CB(self,event=None):
        #
        #   called when the tuning scroll bar is moved
        #
        self.updateCurrentFrequency()
        self.updateTuningLine()

    def frequencyTuningRelease_CB(self, event=None):
        self.mainWindow.theRadio.Set_New_Frequency(self.centerFrequency)
        self.frequencyScrolling = False

    def frequencyTuningPress_CB(self, event=None):
        self.frequencyScrolling = True


    def repeatValueChanged_CB(self, event=None):
        #
        #   Changing the "repeat" count results in this value being changed
        #
        # print("repeatValueChanged_CB, new value:", self.repeat_VAR.get())
        self.remainingCount_VAR.set(self.repeat_VAR.get())

        self.updateScanParameters()


    def bandwidthValueChanged_CB(self, event=None):
        print("bandwidthValueChanged_CB, new value:", self.bandwidthSelected_VAR.get())
        self.updateScanParameters()
        self.recenter_CB()

    def recenter_CB(self):
        #
        #   When the recenter button is pressed, the frequency is changed to the button position and the start/end frequencies
        #   are modified to recognize a new center frequency
        #


        self.lastCenterFrequency = self.centerFrequency
        self.centerFrequency = int(self.currentFrequency_VAR.get())
        self.mainWindow.theRadio.Set_New_Frequency(self.centerFrequency)
        self.frequencyTuning_VAR.set(60)
        self.updateScanParameters()

        self.updateTuningLine()
        self.startSpectrum_CB()


    def runSpectrumScan(self):
        #
        #   kicks off a scan by telling the radio to talk to the DSP and ask for data according
        #   to the previously set parameters
        #

        self.reinitializeValues()       # set peak and average values back to zero
        self.mainWindow.theRadio.startFrequencySpectrumScan(self.startFrequency, int(self.repeat_VAR.get()))

    def parameterStatus(self, status):
        #
        #   Convenience routine to turn all the buttons on or off. When Start button is called, all these
        #   buttons are "disabled". When the scan is done, they are re-enabled.
        #

        self.maxSignal_Combobox.configure(state=status)
        self.minSignal_Combobox.configure(state=status)

        self.bandwidth_Combobox.configure(state=status)
        self.repeat_Combobox.configure(state=status)

        self.recenter_Button.configure(state=status)
        self.startStop_Button.configure(state=status)

        self.applyClose_Button.configure(state=status)
        self.cancel_Button.configure(state=status)

        self.frequencyTuning_Scale.configure(state=status)

        if self.spectrumScanning:
            self.startStopSpectrum_VAR.set("Running")
        else:
            self.startStopSpectrum_VAR.set("Start")




    def startSpectrum_CB(self):
        #
        #   run when start button is pressed
        #

        self.spectrumScanning = True

        self.remainingCount_VAR.set(int(self.repeat_VAR.get()))
        self.parameterStatus("disabled")
        self.runSpectrumScan()


    def scanningComplete(self):
        #
        #   Run after all scanning runs have been completed
        #
        self.spectrumScanning = False
        self.parameterStatus("normal")



    #
    #   resizeCanvas_CB and refreshCanvas work together to deal with any resizing of the canvas.
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
        print("refreshCanvas")
        if self.initUXComplete:
            #
            #   Update canvas size
            #
            self.plotterAvg.refreshCanvas()
            self.plotterPeak.refreshCanvas()
            self.updateTuningLine()

    def checkForFrequencyChange(self):
        if (self.mainWindow.theVFO_Object.getIntPrimaryVFO() != int(self.currentFrequency_VAR.get())) and (self.frequencyScrolling == False):
            self.lastCenterFrequency = self.centerFrequency
            self.centerFrequency = self.mainWindow.theVFO_Object.getIntPrimaryVFO()
            self.currentFrequency_VAR.set(str(self.centerFrequency))
            #
            # Calculate new tuning bar position
            #
            barPos = int((self.centerFrequency - self.startFrequency)/int(self.calculatedSampleSize_VAR.get()))
            self.frequencyTuning_VAR.set(barPos)
            self.updateTuningLine()

        self.frequencyChangeCheckPtr = self.master.after(250,self.checkForFrequencyChange)



    def maxSignal_CB(self, event=None):
        print("maxSignal_CB", self.maxSignal_VAR.get())
        self.refreshCanvas()

    def minSignal_CB(self, event=None):
        print("minSignal_CB", self.minSignal_VAR.get())
        self.refreshCanvas()

    def applyClose_CB(self):
        #
        #   Needs to invoke a mainWindow routine instead of directly calling these attributes
        #
        self.mainWindow.frequencySpectrumMode = "FreqScan"
        self.mainWindow.consumerDSPdata = self.mainWindow
        self.mainWindow.highlightCWorSpectrumBoxes(True)
        self.mainWindow.theRadio.Set_Spectrum_Mode(95)
        self.mainWindow.theRadio.Set_New_Frequency(self.centerFrequency)
        if self.frequencyChangeCheckPtr != None:
            self.master.after_cancel(self.frequencyChangeCheckPtr)
        self.destroy()


    def cancel_CB(self):
        #
        # self.originalFrequency = centerFrequency
        # need to reset frequency to original if user cancels
        #

        self.mainWindow.frequencySpectrumMode = "FreqScan"
        self.mainWindow.consumerDSPdata = self.mainWindow
        self.mainWindow.highlightCWorSpectrumBoxes(True)
        self.mainWindow.theRadio.Set_Spectrum_Mode(95)
        self.mainWindow.theRadio.Set_New_Frequency(self.originalFrequency)
        if self.frequencyChangeCheckPtr != None:
            self.master.after_cancel(self.frequencyChangeCheckPtr)
        self.destroy()


