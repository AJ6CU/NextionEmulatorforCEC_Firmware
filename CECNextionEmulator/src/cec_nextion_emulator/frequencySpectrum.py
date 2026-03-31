#!/usr/bin/python3
"""
Frequency Spectrum

Displays an area of the Frequency showing signal strength

UI source file: frequencySpectrum.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
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
        self.centerFrequency = centerFrequency

        self.startFrequency = None                      # starting frequency for scanning
        self.stopFrequency = None                       # stopping frequency for scanning
        self.bandwidth = None                           # the width of the band being scanned
        self.stepSize = None                            # size of steps (frequency samples)
        self.lastCenterFrequency = None                 # tracks the last center frequency in case it has been changed
                                                        # between scans
        self.MaxADCCount = None                         # Maximum number of times that the ADC can be read.
                                                        # Machine dependent. About
        self.spectrumScanning = None                    # If true, spectrum scanning is running
        #
        #   Plot related values
        #
        self.frequencyLines = {}
        self.frequencyPlotParameters = {
            "y_stretch":2,            # how much to stretch the Y magnitude
            "y_gap":0,                  # gap between lower canvas edge and x axis
            "x_gap":4,                  # gap between left canvas edge and y axis
        }
        self.tuningLine = None

        self.windowResized = False
        self.windowResizedObj = None

        super().__init__(self.master, **kw)


        #
        #   Make sure that a close by the Window manager goes to the same close callback
        #
        self.protocol("WM_DELETE_WINDOW", self.cancel_CB)

        self.initUX()

    def initUX(self):
        # self.title("Frequency Spectrum")
        # self.geometry("800x550")
        self.wait_visibility()  # required on Linux
        self.grab_set()
        self.transient(self.master)

        gv.trimAndLocateWindow(self.master, 0, 0)

        gv.formatCombobox(self.repeat_Combobox, "Arial", "24", "bold")
        gv.formatCombobox(self.bandwidth_Combobox, "Arial", "24", "bold")


        # Update bandwidth to use selected delimiter

        if gv.NUMBER_DELIMITER != '':                   # temporary to handle standalone testing
            localizedBandwidth=[]
            for item in self.bandwidth_Combobox['values']:
                localizedBandwidth.append(item.replace(',', gv.NUMBER_DELIMITER))
            self.bandwidth_Combobox['values']=localizedBandwidth

        #
        #   DEFAULTS
        #

        self.lastCenterFrequency = self.centerFrequency     # save current frequency

        self.MaxADCCount = 120
        self.repeat_VAR.set('10x')
        self.bandwidthSelected_VAR.set('120,000Hz')

        self.spectrumScanning = False           # default to scanning off

        self.updateScanParameters(self.bandwidthSelected_VAR.get())     # Can now format Frequency graphs

        self.frequencyTuning_VAR.set(250)                               # Set scrollbar in middle
        self.currentFrequency_VAR.set(str(self.lastCenterFrequency))    # Set frequency

        self.frequencyPlotCanvas_height = self.frequencyPlotCanvas.winfo_height()
        self.frequencyPlotCanvas_width = self.frequencyPlotCanvas.winfo_width()

    def updateScanParameters(self, newBandwidth):
        #
        #   Need to destroy canvas? and reset
        #
        self.bandwidth = int(newBandwidth.replace(",","").replace(".","").replace("Hz",""))

        self.startFrequency=int(self.centerFrequency - self.bandwidth/2)
        self.startFrequency_VAR.set(str(self.startFrequency))

        self.stopFrequency = int(self.centerFrequency + self.bandwidth/2)
        self.stopFrequency_VAR.set(str(self.stopFrequency))

        self.calculatedSampleSize_VAR.set(int((self.bandwidth / self.MaxADCCount) * 2))

    def genPlotData(self, count):
        buffer = []

        for i in range(count):
            buffer.append(random.randint(0, 255))
        return bytearray(buffer).hex()

    # def calculatePlotParameters(self, canvasWidth):
    #     x_width = canvasWidth // self.MaxADCCount
    #
    #     # what is this fixed constant of "8"???
    #     remainingWidth = canvasWidth - (x_width * self.MaxADCCount) - 8
    #
    #     x_stretch = remainingWidth / self.MaxADCCount
    #
    #     return x_width, x_stretch
    #
    # def calculatePlotBar(self, canvasHeight, x, ymag, x_width, x_stretch, fixedParams):
    #     x0 = (x * x_stretch) + (x * x_width) + fixedParams['x_gap']
    #     y0 = canvasHeight - (ymag * fixedParams['y_stretch'] + fixedParams['y_gap'])
    #     x1 = (x * x_stretch) + (x * x_width) + x_width + fixedParams['x_gap']
    #     y1 = canvasHeight - fixedParams['y_gap']
    #
    #     return x0, y0, x1, y1

    def plot(self, buffer):

        x_width, x_stretch = gv.calculatePlotParameters(self.frequencyPlotCanvas_width, self.MaxADCCount)

        for x in range(self.MaxADCCount):
            ymag = int(buffer[x*2:x*2+2],16)%70

            x0, y0, x1, y1 = gv.calculatePlotBar(self.frequencyPlotCanvas_height, x,  ymag,
                                                   x_width, x_stretch, self.frequencyPlotParameters )

            # draw the bar
            if x in self.frequencyLines:
                self.frequencyPlotCanvas.coords(self.frequencyLines[x][0], x0, y0, x1, y1)
                rectObj = self.frequencyLines[x][0]
            else:
                rectObj=self.frequencyPlotCanvas.create_rectangle(x0, y0, x1, y1, fill="lightgray", outline="lightgray")
            self.frequencyLines[x] = [rectObj, x, x0, x1, y0, y1, ymag]

        if self.tuningLine == None:
            self.tuningLine=self.frequencyPlotCanvas.create_line(self.frequencyPlotCanvas_width/2,
                                                                 self.frequencyPlotCanvas_height,
                                                                 self.frequencyPlotCanvas_width/2, 0,
                                                                 fill="yellow", width=4,dash=(5, 3))
        else:
            self.frequencyPlotCanvas.coords(self.tuningLine, self.frequencyPlotCanvas_width/2,
                                            self.frequencyPlotCanvas_height, self.frequencyPlotCanvas_width/2, 0)

    def updateTuningLine(self,tuningLine,newPos):
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

    def bandwidthValueChanged_CB(self, event=None):
        print("bandwidthValueChanged_CB, new value:", self.bandwidthSelected_VAR.get())
        self.updateScanParameters(self.bandwidthSelected_VAR.get())

    def recenter_CB(self):
        print("recenter_CB")

    def startStopSpectrum_CB(self):
        if self.startStopSpectrum_VAR.get() == "Start":
            self.startStopSpectrum_VAR.set("Stop")
            self.spectrumScanning = False
        else:
            self.startStopSpectrum_VAR.set("Start")
            self.spectrumScanning = True

        self.plotTestData()

    def frequencyPlotCanvas_CB(self, event=None):

        scrollBarSpan = int(self.frequencyTuning_Scale["to"] - self.frequencyTuning_Scale["from"])

        if event.x < self.frequencyLines[0][2]:  #  Check for click to far left outside graph
            pos = int(self.frequencyTuning_Scale["from"])
        else:
            pos = int(self.frequencyTuning_Scale["to"])  #  if we cant find it, must be far right click outside graph
            for i in range(self.MaxADCCount):
                if (event.x >= self.frequencyLines[i][2]<= event.x) and (self.frequencyLines[i][3]>= event.x):
                    pos = int(scrollBarSpan * i/self.MaxADCCount) + int(self.frequencyTuning_Scale["from"])
                    break
        self.frequencyTuning_VAR.set(str(pos))
        self.updateTuningLine(self.tuningLine, pos)
        self.updateCurrentFrequency()

    def resizeCanvas_CB(self, event=None):
        if self.windowResized:
            self.master.after_cancel(self.windowResizedObj)
        else:
            self.windowResized = True
        self.windowResizedObj = self.master.after(100, self.refreshCanvas)



    def refreshCanvas(self):
        if 0 not in self.frequencyLines:
            return

        self.frequencyPlotCanvas_height = self.frequencyPlotCanvas.winfo_height()
        self.frequencyPlotCanvas_width = self.frequencyPlotCanvas.winfo_width()

        x_width, x_stretch = gv.calculatePlotParameters(self.frequencyPlotCanvas_width, self.MaxADCCount)

        for x in range(self.MaxADCCount):

            ymag = self.frequencyLines[x][6]

            x0, y0, x1, y1 = gv.calculatePlotBar(self.frequencyPlotCanvas_height, x, ymag,
                                                   x_width, x_stretch, self.frequencyPlotParameters)

            # draw the bar
            if x in self.frequencyLines:
                self.frequencyPlotCanvas.coords(self.frequencyLines[x][0], x0, y0, x1, y1)
                rectObj = self.frequencyLines[x][0]
            else:
                rectObj = self.frequencyPlotCanvas.create_rectangle(x0, y0, x1, y1, fill="lightgray", outline="lightgray")
            self.frequencyLines[x] = [rectObj, x, x0, x1, y0, y1, ymag]

        if self.tuningLine == None:
            self.tuningLine = self.frequencyPlotCanvas.create_line(canvasWidth / 2, canvasHeight, canvasWidth / 2, 0,
                                                                   fill="yellow", width=4, dash=(5, 3))
        else:
            self.updateTuningLine(self.tuningLine, int(self.frequencyTuning_VAR.get()))


    def plotTestData(self):
        buffer = self.genPlotData(self.MaxADCCount)
        self.plot(buffer)

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

