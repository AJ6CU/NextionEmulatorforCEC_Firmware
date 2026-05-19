#!/usr/bin/python3
"""
Band Scanner

Scans up to three selected bands for signals.

UI source file: bandScanner.ui
"""
import tkinter as tk
import tkinter.ttk as ttk

from barPlotter import barPlotter
from tkinter import messagebox

import bandScannerui as baseui

import globalvars as gv


#
# Manual user code
#

class graphObject(barPlotter):

    def __init__(self, targetLabelFrame, canvasObj=None, totalX=120, maxY=70,
                 barColor="yellow", X_GAP=4, Y_GAP=0, currentMax=0, currentMin=0, **kw):

        self.targetLabelFrame = targetLabelFrame
        self.canvasObj = canvasObj
        self.totalX = totalX
        self.maxY = maxY

        self.yDivider = 0

        self.barColor = barColor
        self.X_GAP = X_GAP
        self.Y_GAP = Y_GAP
        self.currentMax = currentMax
        self.currentMin = currentMin

        self.averageBuffer = bytearray(self.totalX)
        self.processDataCount = 0

        self.bandID = None
        self.bandStart = None
        self.bandEnd = None
        self.activateFlag = False
        self.scrollbarSize = None

        super().__init__(self.targetLabelFrame, self.canvasObj, self.totalX, self.maxY, self.X_GAP, self.Y_GAP,
                         self.currentMax, self.currentMin, self.barColor, **kw)

    def deactivate(self):
        self.bandID = None
        self.bandStart = None
        self.bandEnd = None

        self.activateFlag = False
        self.targetLabelFrame.configure(text="Select Band...")


    def activate(self, bandID, bandStart, bandSampleSize, maxY=70, scrollbarSize=120):
        self.bandID = bandID
        self.bandStart = bandStart
        self.bandSampleSize = bandSampleSize
        self.maxY = maxY
        self.scrollbarSize = scrollbarSize

        self.bandEnd = self.bandStart + (self.bandSampleSize * scrollbarSize)

        print("band:", self.bandStart, gv.bandEnd[bandID], "actual end", self.bandStart + (self.bandSampleSize * 120))

        self.activateFlag = True
        self.targetLabelFrame.configure(text=self.bandID.replace("Band", "Band: "))

    def get_bandID(self):
        return self.bandID

    def getFrequency(self, scrollbarPosition):
        pass

    def setFrequency(self, scrollbarPosition):
        return self.bandStart + (self.bandSampleSize * scrollbarPosition)

    def available(self):
        return not self.activateFlag

    def activated(self):
        return self.activateFlag

    def processData(self, buffer):

        byteBuffer = bytearray.fromhex(buffer)
        self.processDataCount += 1

        for x, y in enumerate(byteBuffer):

            tmp = int(round(self.averageBuffer[x] + ((y - self.averageBuffer[x]) / self.processDataCount)))

            if tmp > 255:
                print("tmp too big, tmp")
            self.averageBuffer[x] = tmp




    def drawHighLightBars(self):
        self.drawHighLightBars(int(self.frequencyTuning_VAR.get()))

    def displayData(self, buffer):

        (super).process_Data(self, self.buffer)             # yDivider is defaulted to 0

        self.plotter.drawHighLightBars()
        self.processDataCount = 0
        self.averageBuffer = bytearray(self.totalX)




class bandScanner(baseui.bandScannerUI):


    def __init__(self,  master=None, mainWindow=None, **kw):
        self.master = master                            # pointer to the root master.Needed for scheduling "after" events
        self.mainWindow = mainWindow

        self.lastFrequency = None                 # tracks the last center frequency in case it has been changed
                                                        # between scans

        self.frequencyScrolling = False                 # tracks when the scrollbar is being used to adjust frequency
                                                        # turns on when button 1 pressed, off when released

        #
        #   DEFAULTS
        #


        self.MaxADCCount = 120  # Maximum number of times that the ADC can be read.
                                # CEC hardwires 120 here
        self.repeatCount = 3    # Scan each band 3x

        self.FREQ_Y_MAX = 70  # maximum value of Y values

        self.numberBandsChecked = 0     # Total number of bands checked

        self.targetGraph = [None]  * 3
        self.scanlist = []              # used to identify which targetGraphs are acticated and require band scans
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

        # self.initUXComplete = False                 # used to avoid errors generated by incoming data prior to completion
        #                                             # of initialization of object

        super().__init__(self.master, **kw)


        #
        #   Make sure that a close by the Window manager goes to the same close callback
        #
        self.protocol("WM_DELETE_WINDOW", self.close_CB)

        self.initUX()           # This deals with any initiation that needs to be done after the Object is fully
                                # instantiated.

    def initUX(self):
        # self.title("Frequency Spectrum")
        self.geometry("825x675")

        self.wait_visibility()  # required on Linux
        self.grab_set()
        self.transient(self.master)



        self.frequencyTuning_VAR.set(60)                                                # Set scrollbar to middle


        self.lastFrequency = self.mainWindow.theVFO_Object.getIntPrimaryVFO()
        #
        #   Set the defaults for scanning
        #
        #   repeatCount = 3   - scan 3 times reporting the average
        #   self.MaxADCCount = 120  constant, always get back 120 slots
        #   100 - this is the bandwidth  100 x 20 = 2000
        #
        self.mainWindow.theRadio.updateFrequencySpectrumOptions(self.repeatCount, 0, self.MaxADCCount, 100)
        #
        #   Instantiate the 3 objects to do the plotting
        #
        self.targetGraph[0] = graphObject(self.band0_Labelframe, self.band0Plot_Canvas)
        self.targetGraph[1] = graphObject(self.band1_Labelframe, self.band1Plot_Canvas)
        self.targetGraph[2] = graphObject(self.band2_Labelframe, self.band2Plot_Canvas)


        self.initUXComplete = True


    def resizeCanvas_CB(self, event=None):
        pass


    def frequencyTuningRelease_CB(self, event=None):
        for i in range(len(self.targetGraph)):
            if self.targetGraph[i].available():
                return
            else:
                f=gv.formatVFO(str(self.targetGraph[i].setFrequency(int(self.frequencyTuning_VAR.get()))))
                getattr(self, "band"+str(i)+"Frequency_VAR").set(str(f))
        pass

    def bandGo_CB(self, widget_id):
        print("bandGo_CB: widget_id=", widget_id)

    def allocateGraphObj(self, bandID, bandStart, bandSampleSize, maxY=70, scrollbarSize=120):
        for i in range(len(self.targetGraph)):
            if self.targetGraph[i].available():
                self.targetGraph[i].activate(bandID, bandStart, bandSampleSize, self.FREQ_Y_MAX, scrollbarSize)
                f=gv.formatVFO(str(self.targetGraph[i].setFrequency(int(self.frequencyTuning_VAR.get()))))
                getattr(self, "band"+str(i)+"Frequency_VAR").set(f)
                return True

        #
        #   If it falls thru, no available slots. Display warning message
        #

        messagebox.showwarning(title="No Available Graph Areas",
            message="Attempt to allocate more than 3 bands for scanning", parent=self,
            detail="You must first free up a band and then try again.")
        return False

    def releaseGraphObj(self, bandID):
        for i in range(len(self.targetGraph)):
            if self.targetGraph[i].get_bandID() == bandID:
                self.targetGraph[i].deactivate()
                getattr(self, "band" + str(i) + "Frequency_VAR").set("")
                return True
        #
        #   If it dropped thru, tried to deactivate a bandID that was not found.
        #
        return False


    def band_Checked_CB(self, widget_id):
        print("band checked callback, widget_id=", widget_id)

        if getattr(self,widget_id+"_Checked_VAR").get() == '1':
            #
            #   Trying to allocate this band. Allocate it. If True, success
            #
            if self.allocateGraphObj(widget_id,gv.bandStart[widget_id], gv.bandSampleSize[widget_id],
                                     self.FREQ_Y_MAX, self.MaxADCCount):
                #
                #   True indicates successful allocation. Can just return
                #
                return
            else:
                #
                #   False indicates no available slots. Error message already generated to free up slots
                #
                getattr(self,widget_id+"_Checked_VAR").set('0')
                return
        else:
            #
            #   Trying to deactivate a graphobject
            #
            if self.releaseGraphObj(widget_id):
                return
            else:
                print("trying to release a band that is not allocated, band=", widget_id)
                return

    def processData(self,buffer):
        self.processDataCount += 1

        if self.processDataCount == self.repeatCount:
            self.displayData()

    def process_Spectrum_Data(self,buffer):
        pass


    def scan_CB(self):
        print("scan_CB")
        self.spectrumScanning = True
        self.parameterStatus("disabled")
        for i in range(len(self.targetGraph)):
            if self.targetGraph[i].activated():         # if this GraphObject is activated, add it to list to process
                self.scanlist.append(i)
                self.mainWindow.theRadio.startFrequencySpectrumScan()  ##WRONG! Not done


        self.mainWindow.theRadio.startFrequencySpectrumScan(self.startFrequency, int(self.repeat_VAR.get()))


    def parameterStatus(self, status):
        #
        #   Convenience routine to turn all the buttons on or off. When Start button is called, all these
        #   buttons are "disabled". When the scan is done, they are re-enabled.
        #


        self.band1GO_Button.configure(state=status)
        self.band2GO_Button.configure(state=status)
        self.band3GO_Button.configure(state=status)


        self.scan_Button.configure(state=status)
        self.close_Button.configure(state=status)

        self.Band160m.configure(state=status)
        self.Band80m.configure(state=status)
        self.Band40m.configure(state=status)
        self.Band30m.configure(state=status)
        self.Band20m.configure(state=status)
        self.Band17m.configure(state=status)
        self.Band15m.configure(state=status)
        self.Band12m.configure(state=status)
        self.Band10m.configure(state=status)

        self.frequencyTuning_Scale.configure(state=status)

        if self.spectrumScanning:
            self.scan_Button_VAR.set("Running")
        else:
            self.scan_Button_VAR.set("Scan")



    def close_CB(self):
        #
        #   Needs to invoke a mainWindow routine instead of directly calling these attributes
        #
        self.mainWindow.frequencySpectrumMode = "FreqScan"
        self.mainWindow.consumerDSPdata = self.mainWindow
        self.mainWindow.highlightCWorSpectrumBoxes(True)
        self.mainWindow.theRadio.Set_Spectrum_Mode(95)
        self.mainWindow.theRadio.Set_New_Frequency(self.lastFrequency)
        self.mainWindow.consumerSpectrumdata = None
        print("reseting frequency=", self.lastFrequency)
        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = bandScanner(root)
    root.mainloop()
