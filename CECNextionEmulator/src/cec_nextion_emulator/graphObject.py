import tkinter as tk
import tkinter.ttk as ttk

from barPlotter import barPlotter

import globalvars as gv
#
#   This object (graphObject) is used by bandScanner to manage the allocation, deallocation, updating of a bandGraph
#   object. As such, it is created by bandScanner and a bandGraph is assigned to it to manage
#
#   When a user changes the bandStart scrollbar, a callback is made into the appropriate graphObject so that the
#   start/end points for the scan can be calculated. These new values are then pushed back into the bandGraph for display
#
#   If the user moves the tunning scrollbar in the bandScanner window (the one at the bottom), the scan start is fetched
#   from the attached bandGraph and passed up to the bandScanner window so that the current frequency can be updated
#   for the band.
#   There needs to be a callback associated with updating this current frequency since a change in the begin/end of the
#   scanning region can effect what the current frequency is for the band.
#


class graphObject(barPlotter):

    def __init__(self, band, updateFreqField_callback,  windowResized_callback, masterFreqScrollbar, totalX=120, maxY=70,
                 barColor="yellow", X_GAP=4, Y_GAP=0, currentMax=0, currentMin=0, **kw):

        self.band = band                # object pointer to the bandGraph associated with this GraphObject
                                        # the bandGraph is created in the parent (bandScanner) object
                                        # and then attached to a graphObject

        self.updateFreqField_CB = updateFreqField_callback
                                        # this is a callback in bandScanner to update the Frequency
                                        # for the band.
        self.windowResized_CB = windowResized_callback

        self.masterFreqScrollbar = masterFreqScrollbar
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

        super().__init__(self.band, self.band.bandPlot_Canvas, self.totalX, self.maxY, self.X_GAP, self.Y_GAP,
                         self.currentMax, self.currentMin, self.barColor, **kw)
        #
        #   Attach the callback within this GraphObject to process the movement of the scrollbar
        #   from within the bandGraph Object.
        #
        self.band.attachScrollbar_CB(self.updateScanRange)      # this attaches a callback within graphObject
                                                                # updateScanRange to the individual scrollbar
                                                                # within the bandGraph. When the scrollbar is
                                                                # moved, this routine is called to adjust the scanning
                                                                # range for this band
        self.band.attachWindowResized_CB(self.windowResized_CB)
    #
    #   Activates a graphObject when a band is assigned to a particular Ham band
    #
    def activate(self, bandID, bandStart, bandEnd, bandwidth, maxY=70, scrollbarSize=120):
        self.bandID = bandID
        self.bandStart = bandStart
        self.bandEnd = bandEnd
        self.bandwidth = bandwidth
        self.maxY = maxY
        self.scrollbarSize = scrollbarSize

        self.updateScrollbarRange(self.band, self.bandStart, self.bandEnd, self.bandwidth * self.scrollbarSize)
        self.band.scanningRange_VAR.set("")

        self.updateScanRange(0)             # sets scrollbar for scan range to lowest point in


        # print("band:", self.bandStart, gv.bandEnd[bandID], "actual end", self.bandStart + (self.bandwidth * 120))

        self.activateFlag = True
        self.band.configure(text=self.bandID.replace("Band", "Band: "))
        self.band.bandStart_Scale.configure(state="normal")

    #
    #   Deactivates a band in the bandScanner when the user deselects it. This resets values to their defaults
    #
    def deactivate(self):
        self.bandID = None
        self.bandStart = None
        self.bandEnd = None

        self.activateFlag = False
        self.band.scanningRange_VAR.set("")
        self.band.bandRange_VAR.set("")
        self.band.configure(text="Select Band...")
        self.band.bandStart_Scale.configure(state="disabled")
        # self.updateScanRange(0)

    #
    #   This routine is used to update the scanning range for the bandScanner. Since the maximum is 240,000hz
    #   there is a scrollbar for each band that allows the user to adjust the start point.
    #   There is some additional complexity here as we want to maximize the amount of band to scan. This means
    #   that begin point of the scan needs to be no more than 240,000 from the end point. And in the case where the
    #   full band is less than 240,000hz (e.g. 160M), then the scale needs to be deactivated and the begin/end points
    #   set to the actual limits of the band.
    #
    #   After the band range is adjusted, a callback is made to the bandScanner to update the current frequency for
    #   the band based on the new start scan point as well as the position of the main tuning scrollbar in the
    #   bandScanner window.
    #

    def updateScanRange(self, pos, Event=None):
        self.bandScanStart = self.bandStart + (round(float(pos)) * self.bandwidth)
        self.bandScanEnd = self.bandScanStart + (self.bandwidth * self.scrollbarSize)
        #
        #   Make sure that the displayed scanned range is always within the band
        #
        if self.bandScanEnd > self.bandEnd:
            self.bandScanEnd = self.bandEnd
            self.bandScanStart = self.bandScanEnd - (self.bandwidth * self.scrollbarSize)
            if self.bandScanStart < self.bandStart:
                self.bandScanStart = self.bandStart

        self.band.scanningRange_VAR.set("Scanning Range: " + gv.formatVFO(str(self.bandScanStart)) + " - " + gv.formatVFO(str(self.bandScanEnd)))

        self.band.bandRange_VAR.set("Band Range: " + gv.formatVFO(str(self.bandStart)) + " - " + gv.formatVFO(str(self.bandEnd)))
        self.updateFreqField_CB(self)


    #
    #   Need to make scale disabled state more obvious...
    #
    def updateScrollbarRange(self, band, bandStart, bandEnd, bandwidth):
        if (bandEnd - bandStart) < bandwidth:
            band.bandStart_Scale.configure(state="disabled")
        else:
            band.bandStart_Scale.configure(state="normal")
        bandSpread = bandEnd - bandStart
        scaleLength = (bandSpread - bandwidth)/ self.bandwidth
        # scaleEnd = scaleLength - 1
        band.bandStart_Scale.configure(to=int(scaleLength))
        # print("updateScaleRange", int(scaleLength))
        # band.updateFrequency_CB()






    def get_bandID(self):
        return self.bandID

    def getFrequency(self, scrollbarPosition):
        if scrollbarPosition+1 == self.scrollbarSize:
            return self.bandScanEnd
        elif scrollbarPosition == 0:
            return self.bandScanStart
        else:
            return gv.roundToNearest(self.bandStart + (self.bandwidth * scrollbarPosition), self.bandwidth)
    #
    #   Get routine that just returns the starting frequency for the band scanning
    #
    def getStartScanF(self):
        return self.bandScanStart

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
        super().drawHighLightBars(int(self.masterFreqScrollbar.get()))

    def displayData(self, buffer):

        # print("displayData, buffer=", buffer)
        super().process_Data(buffer)             # yDivider is defaulted to 0

        self.drawHighLightBars()
        # self.processDataCount = 0
        # self.averageBuffer = bytearray(self.totalX)



