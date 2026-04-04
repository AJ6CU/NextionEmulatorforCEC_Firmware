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
import time

import mystyles
import globalvars as gv


#
# Manual user code
#

class frequencySpectrum(baseui.frequencySpectrumUI):
    def __init__(self,  master=None, mainWindow=None, centerFrequency=None, **kw):
        self.master = master
        self.mainWindow = mainWindow
        self.centerFrequency = centerFrequency          # the current (VFO) frequency is passed and saved

        self.startFrequency = None                      # starting frequency for scanning
        self.stopFrequency = None                       # stopping frequency for scanning
        self.bandwidth = None                           # the width of the band being scanned
        self.stepSize = None                            # size of steps (frequency samples)
        self.lastCenterFrequency = None                 # tracks the last center frequency in case it has been changed
                                                        # between scans
        self.tuningLine = None                          # used to save the tuning line object

        #
        #   DEFAULTS
        #

        self.lastCenterFrequency = self.centerFrequency     # save current frequency, need this to check if current
                                                            # frequency has been changed

        self.MaxADCCount = 120  # Maximum number of times that the ADC can be read.
                                # Machine dependent. About

        self.FREQ_X_GAP = 4  # gap between left canvas edge and y axis
        self.FREQ_Y_GAP = 0  # gap between lower canvas edge and x axis
        self.FREQ_Y_MAX = 255  # maximum value of Y values

        self.frequencyLineObj = [None] * self.MaxADCCount * 1
        self.frequencyLineYmag = [None] * self.MaxADCCount * 1
        self.frequencyLineX0 = [None] * self.MaxADCCount * 1
        self.frequencyLineX1 = [None] * self.MaxADCCount * 1



        self.spectrumScanning = False               # default to scanning off

        self.windowResized = False                  # these two variables are used to handle resizing of screen
        self.windowResizedObj = None                # while window is active. When the resized is detected,
                                                    # the windowResized flag is set to true and a future
                                                    # event is created to eventually update the window after 100ms
                                                    # Each time the reseize event is called, the current future event
                                                    # is deleted and a new one is scheduled. Only after 100 ms of no
                                                    # new resize, is the scheduled event finally executed, the graph is
                                                    # updated and the flag is set back to False.

        super().__init__(self.master, **kw)


        #
        #   Make sure that a close by the Window manager goes to the same close callback
        #
        self.protocol("WM_DELETE_WINDOW", self.cancel_CB)

        self.initUX()           # This deals with any initiation that needs to be done after the Object is fully
                                # instantiated.

    def initUX(self):
        # self.title("Frequency Spectrum")
        # self.geometry("800x550")
        self.wait_visibility()  # required on Linux
        self.grab_set()
        self.transient(self.master)

        gv.trimAndLocateWindow(self.master, 0, 0)

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


        self.repeat_VAR.set('10x')
        self.bandwidthSelected_VAR.set('120,000Hz')
        self.minSignal_VAR.set('0')
        self.maxSignal_VAR.set('255')

        self.bandwidthSelected_VAR.set('120,000Hz')

        self.updateScanParameters(self.bandwidthSelected_VAR.get())     # Can now format Frequency graphs

        self.frequencyTuning_VAR.set(250)                               # Set scrollbar in middle
        self.currentFrequency_VAR.set(str(self.lastCenterFrequency))    # Set frequency

        self.frequencyPlotCanvas_height = self.frequencyPlotCanvas.winfo_height()
        self.frequencyPlotCanvas_width = self.frequencyPlotCanvas.winfo_width()

    def updateScanParameters(self, newBandwidth):
        #
        #   When the bandwidth is changed, this routine is called to re-establish the scanning
        #   TODO check if scan running, stop it, reset stuff, and then rerun
        #
        self.bandwidth = int(newBandwidth.replace(",","").replace(".","").replace("Hz",""))

        self.startFrequency=int(self.centerFrequency - self.bandwidth/2)
        self.startFrequency_VAR.set(str(self.startFrequency))

        self.stopFrequency = int(self.centerFrequency + self.bandwidth/2)
        self.stopFrequency_VAR.set(str(self.stopFrequency))

        self.calculatedSampleSize_VAR.set(int((self.bandwidth / self.MaxADCCount) * 2))

    def genPlotData(self, count):
        #
        #   Test routine to just generate random data to plot
        #

        buffer = []

        for i in range(count):
            buffer.append(random.randint(0, 255))
        return bytearray(buffer).hex()

    def plot(self, buffer):
        #
        # This plots the frequency ADC values. Uses generic routines to figure out sizes of canvas and bar sizes
        #

        x_width, x_stretch, y_stretch = gv.calculatePlotParameters(self.frequencyPlotCanvas_width, self.MaxADCCount,
                                                                      self.FREQ_X_GAP,
                                                                      self.frequencyPlotCanvas_height,
                                                                      int(self.maxSignal_VAR.get())-int(self.minSignal_VAR.get()),
                                                                      self.FREQ_Y_GAP)

        for x in range(self.MaxADCCount):
            ymag = int(buffer[x*2:x*2+2],16)
            yplot = ymag

            if yplot < int(self.minSignal_VAR.get()):
                yplot = 0
            # yplot = yplot + (self.FREQ_Y_MAX - int(self.maxSignal_VAR.get()))
            if yplot > int(self.maxSignal_VAR.get()):
                yplot = int(self.maxSignal_VAR.get())

            x0, y0, x1, y1 = gv.calculatePlotBar(self.frequencyPlotCanvas_height, x,  yplot, x_width, x_stretch,
                                                 self.FREQ_X_GAP, y_stretch, self.FREQ_Y_GAP)

            # draw the bar
            if self.frequencyLineObj[x] != None:            # if bar exists, then adjust coordinates for new values
                self.frequencyPlotCanvas.coords(self.frequencyLineObj[x], x0, y0, x1, y1)
            else:                                           # If this is the first time, then create the bar
                self.frequencyLineObj[x] = self.frequencyPlotCanvas.create_rectangle(x0, y0, x1, y1, fill="lightgray",
                                                                                     outline="lightgray")
            #
            #   Save y magnitude for resize event
            #   Save x0,x1 for identifying location of a mouse click on the graph
            #
            self.frequencyLineYmag[x] = ymag
            self.frequencyLineX0[x] = x0
            self.frequencyLineX1[x] = x1
        #
        #   Need to set the tuning line. If it is the first time, create it and save a pointer to the object
        #   If it is a second time, then can just use the existing line
        #   TODO Is this if needed? I think this is always None here???
        #
        if self.tuningLine == None:
            self.tuningLine=self.frequencyPlotCanvas.create_line(self.frequencyPlotCanvas_width/2,
                                                                 self.frequencyPlotCanvas_height,
                                                                 self.frequencyPlotCanvas_width/2, 0,
                                                                 fill="yellow", width=4,dash=(5, 3))
        else:
            self.frequencyPlotCanvas.coords(self.tuningLine, self.frequencyPlotCanvas_width/2,
                                            self.frequencyPlotCanvas_height, self.frequencyPlotCanvas_width/2, 0)
        #
        #   Track count received.  If continous, then generate a request for a new record
        #
        if self.repeat_VAR.get() == "Cont.":  # continous running until stopped
            if self.spectrumScanning == True:
                # self.runSpectrumScan(1)
                self.master.after(100, self.runSpectrumScan, 1)
            else:
                self.scanningComplete()
        else:
            self.remainingCount_VAR.set(str(int(self.remainingCount_VAR.get())-1))
            if int(self.remainingCount_VAR.get()) == 0:
                self.scanningComplete()


    def updateTuningLine(self,tuningLine,newPos):
        #
        #   Used to update Tuning line when a change is detected by either the move of the scroll bar or click on graph
        #
        scrollBarSpan = int(self.frequencyTuning_Scale["to"] - self.frequencyTuning_Scale["from"])
        pos = int((self.frequencyPlotCanvas_width-4) * (newPos/scrollBarSpan))
        if pos >= self.frequencyPlotCanvas_width:
            pos = self.frequencyPlotCanvas_width -4
        elif pos <= 0:
            pos=4
        self.frequencyPlotCanvas.coords(tuningLine, pos,self.frequencyPlotCanvas_height, pos, 0)

    def updateCurrentFrequency(self):
        scrollBarSpan = int(self.frequencyTuning_Scale["to"] - self.frequencyTuning_Scale["from"])
        self.currentFrequency = int((self.bandwidth * (int(self.frequencyTuning_VAR.get())/scrollBarSpan))+self.startFrequency)
        self.currentFrequency_VAR.set(str(self.currentFrequency))

    def frequencyTuning_CB(self,event=None):
        self.updateCurrentFrequency()
        self.updateTuningLine(self.tuningLine,int(self.frequencyTuning_VAR.get()))


    def repeatValueChanged_CB(self, event=None):
        print("repeatValueChanged_CB, new value:", self.repeat_VAR.get())
        self.remainingCount_VAR.set(self.repeat_VAR.get().replace("X",""))
        #
        #   100 is step count when multiplied by 20 gets the jump on the scan
        #
        #self.mainWindow.theRadio.updateFrequencySpectrumOptions(int(self.repeat_VAR.get().replace("X","")),0,
                                                                # self.MaxADCCount,100)

    def bandwidthValueChanged_CB(self, event=None):
        print("bandwidthValueChanged_CB, new value:", self.bandwidthSelected_VAR.get())
        self.updateScanParameters(self.bandwidthSelected_VAR.get())
        self.mainWindow.theRadio.updateFrequencySpectrumOptions(int(self.repeat_VAR.get().replace("X", "")), 0,
                                                                self.MaxADCCount, 100)

    def recenter_CB(self):
        print("recenter_CB")

    def runSpectrumScan(self,count):
        # self.mainWindow.theRadio.startFrequencySpectrumScan(count, 0, self.MaxADCCount, 100)
        print("runSpectrumScan called, count:", count)
        self.plotTestData()

    def startStopSpectrum_CB(self):
        if self.startStopSpectrum_VAR.get() == "Start":
            self.spectrumScanning = True
            if self.repeat_VAR.get() == "Cont.":        # continous running until stopped
                self.startStopSpectrum_VAR.set("Stop")
                self.runSpectrumScan(1)
            else:
                self.startStopSpectrum_VAR.set("Running")
                self.startStop_Button.configure(state=tk.DISABLED)
                self.remainingCount_VAR.set(int(self.repeat_VAR.get().replace("x", "")))
                self.runSpectrumScan(int(self.repeat_VAR.get().replace("x", "")))

        else:
            self.startStopSpectrum_VAR.set("Start")
            self.spectrumScanning = False

    def scanningComplete(self):
       self.startStop_Button.configure(state=tk.NORMAL)
       self.spectrumScanning = False
       self.startStopSpectrum_VAR.set("Start")


    def frequencyPlotCanvas_CB(self, event=None):

        scrollBarSpan = int(self.frequencyTuning_Scale["to"] - self.frequencyTuning_Scale["from"])

        if event.x < self.frequencyLineX0[0]:  #  Check for click to far left outside graph
            pos = int(self.frequencyTuning_Scale["from"])
        else:
            pos = int(self.frequencyTuning_Scale["to"])  #  if we cant find it, must be far right click outside graph
            for i in range(self.MaxADCCount):
                if (event.x >= self.frequencyLineX0[i] <= event.x) and (self.frequencyLineX1[i] >= event.x):
                    pos = int(scrollBarSpan * i/self.MaxADCCount) + int(self.frequencyTuning_Scale["from"])
                    break
        self.frequencyTuning_VAR.set(str(pos))
        self.updateTuningLine(self.tuningLine, pos)
        self.updateCurrentFrequency()

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
        #
        #   Update canvas size
        #
        self.frequencyPlotCanvas_height = self.frequencyPlotCanvas.winfo_height()
        self.frequencyPlotCanvas_width = self.frequencyPlotCanvas.winfo_width()

        if self.frequencyLineObj[0] == None:        # if nothing plotted, just return
            return

        print("actual refreshing")
        x_width, x_stretch, y_stretch = gv.calculatePlotParameters(self.frequencyPlotCanvas_width, self.MaxADCCount,
                                                                  self.FREQ_X_GAP,
                                                                  self.frequencyPlotCanvas_height,
                                                                  int(self.maxSignal_VAR.get())-int(self.minSignal_VAR.get()),
                                                                  self.FREQ_Y_GAP)
        for x in range(self.MaxADCCount):

            ymag = self.frequencyLineYmag[x]
            yplot = ymag

            if yplot < int(self.minSignal_VAR.get()):
                yplot = 0


            if yplot > int(self.maxSignal_VAR.get()):
                yplot = int(self.maxSignal_VAR.get())
            # yplot = yplot + (self.FREQ_Y_MAX - int(self.maxSignal_VAR.get()))

            x0, y0, x1, y1 = gv.calculatePlotBar(self.frequencyPlotCanvas_height, x,  yplot, x_width, x_stretch,
                                                 self.FREQ_X_GAP, y_stretch, self.FREQ_Y_GAP)

            # draw the bar
            if self.frequencyLineObj[x] != None:
                self.frequencyPlotCanvas.coords(self.frequencyLineObj[x], x0, y0, x1, y1)
            else:
                self.frequencyLineObj[x] = self.frequencyPlotCanvas.create_rectangle(x0, y0, x1, y1, fill="lightgray", outline="lightgray")
            self.frequencyLineYmag[x] = ymag
            self.frequencyLineX0[x] = x0
            self.frequencyLineX1[x] = x1

        #
        #
        #
        if self.tuningLine == None:
            self.tuningLine = self.frequencyPlotCanvas.create_line(self.frequencyPlotCanvas_width / 2,
                                                                   self.frequencyPlotCanvas_height,
                                                                   self.frequencyPlotCanvas_width / 2, 0,
                                                                   fill="yellow", width=4, dash=(5, 3))
        else:
            self.updateTuningLine(self.tuningLine, int(self.frequencyTuning_VAR.get()))


    def plotTestData(self):
        buffer = self.genPlotData(self.MaxADCCount)
        self.plot(buffer)

    def maxSignal_CB(self, event=None):
        print("maxSignal_CB", self.maxSignal_VAR.get())
        self.refreshCanvas()

    def minSignal_CB(self, event=None):
        print("minSignal_CB", self.minSignal_VAR.get())
        self.refreshCanvas()

    def applyClose_CB(self):
        print("applyClose_CB")
        self.destroy()


    def cancel_CB(self):
        print("cancel_CB")
        self.destroy()




myroot=None
mainWindow=None

def updatePlot(root, widget):
    widget.plotTestData()
    myroot.after(100, updatePlot,root, widget)

def launch_widget():
    global myroot
    widget= frequencySpectrum(myroot,mainWindow, 14150000)
    # myroot.after(50, updatePlot, myroot, widget)


if __name__ == "__main__":
    myroot = tk.Tk()
    mystyles.setup_ttk_styles(myroot)

    Launch_Button = ttk.Button(myroot, text="Launch")
    Launch_Button.configure(text='Launch')
    Launch_Button.configure(command=launch_widget)
    Launch_Button.pack(side="top")


    myroot.mainloop()

