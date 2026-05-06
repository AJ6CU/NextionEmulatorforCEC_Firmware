import tkinter as tk
import tkinter.ttk as ttk
import globalvars as gv

class barPlotter:
    def __init__(self, parent, canvasObj, totalX, maxY, X_GAP=4, Y_GAP=0, currentMax=0, currentMin=0):
        self.parent = parent
        self.canvasObj = canvasObj
        self.totalX = totalX
        self.maxY = maxY
        self.X_GAP = X_GAP  # gap between left canvas edge and y axis
        self.Y_GAP = Y_GAP  # gap between lower canvas edge and x axis

        self.xWidth = None      # calculated width of bar based on canvas size, number of bars and gaps between bars
        self.xStretch = None    # Calculated multiple based number of X values, width of canvas, gaps, etc
        self.yStretch = None    # Calculated multiple based on maximum Y and the height of the canvas

        self.currentMax = currentMax    # Max Y value seen
        self.currentMin = currentMin    # Smallest Y value seen
        
        self.canvas_height = self.canvasObj.winfo_height()
        self.canvas_width = self.canvasObj.winfo_width()
        print("self.canvas_height=", self.canvas_height, "self.canvas_width=", self.canvas_width)

        #
        #   Following used to save object pointers to bars and lines drawn so we can just move them
        #   as their locations (tuning lines) or magnitudes change
        #
        self.barObj = [None] * self.totalX * 1      # pointer to the bar (rectangle created)
        self.barY = [None] * self.totalX * 1        # height of the bar
        self.barX0 = [None] * self.totalX * 1       # first point of a bar along the x axis
        self.barX1 = [None] * self.totalX * 1       # second point of a bar along the x axis

        self.tuningLine1 = None  # used to save the tuning line object
        self.tuningLine2 = None  # used to save the tuning line object

    


    def calculatePlotParameters(self):
        #
        #   Routine calculates parameters of the bar chart based on various factors
        #
        self.xWidth = self.canvas_width // self.totalX      # "//" divides and rounds down to the integrer

        # what is this fixed constant of "8"???
        remainingWidth = self.canvas_width - (self.xWidth * self.totalX) - (2 * self.X_GAP)

        self.xStretch = remainingWidth / self.totalX
        self.yStretch = (self.canvas_height - self.Y_GAP) / self.maxY


    def calculatePlotBar(self, x, ymag):
        # canvasHeight = the height of the canvas in pixels
        # x = number of the bar being plotted
        # ymag = actual magnitude of the bar
        # x_width = width of the bar
        # x_stretch = multiply factor to make total bars just fit on the canvas
        # fixedParms = parameters that are "fixed" regardless of number of bars plotted
        x0 = round((x * self.xStretch) + (x * self.xWidth) + self.X_GAP)
        y0 = round(self.canvas_height - ((ymag * self.yStretch) + self.Y_GAP))
        x1 = round((x * self.xStretch) + (x * self.xWidth) + self.xWidth + self.X_GAP)
        y1 = round(self.canvas_height - self.Y_GAP)
        return x0, y0, x1, y1

    def process_Data(self, buffer, yDivider=0):
        # print("buffer size=", len(buffer))
        #
        #   Need to check on whether the Switch for DSP is still on.
        #   Can get into a race condition on turning it off where you delete the bars on canvas
        #   and there is still one more coming thru that turns them back on again
        #
        if gv.config.get_DSP_Switch() == "True":

            self.calculatePlotParameters()              # calculate the fixed parameters of the chart

            # print("in plotter", buffer[0], type(buffer[0]))
            if type(buffer[0]) == str:
                byteBuffer = bytearray.fromhex(buffer)      #This gives us an array of hex bytes
            else:
                byteBuffer = buffer
            for x, y in enumerate(byteBuffer):

                ymag = y>>yDivider
                if ymag < 0:
                    ymag = 0
                elif (ymag > self.maxY):
                        ymag = self.maxY

                if ymag < self.currentMin:
                    self.currentMin = ymag
                    # self.frequencyLowValue_VAR.set(str(currentMin))
                elif ymag > self.currentMax:
                    self.currentMax = ymag
                    # self.frequencyHighValue_VAR.set(str(currentMax))
                # print("Bar X=", x, "Y=", ymag)
                self.drawBars(x, ymag)


    def drawBars(self,x,y):

        # calculate rectangle coordinates (integers) for each bar
        # x0 = x * x_stretch + x * x_width + x_gap
        # y0 = c_height - (ymag * y_stretch + y_gap)
        # x1 = x * x_stretch + x * x_width + x_width + x_gap
        # y1 = c_height - y_gap

        x0, y0, x1, y1 = self.calculatePlotBar(x,y)

        # draw the bar
        if self.barObj[x] == None:  # if the bar doesn't yet exist, create it
            self.barObj[x] = self.canvasObj.create_rectangle(x0, y0, x1, y1, fill="yellow",
                                                                   outline="yellow", tags="bars")
        else:                       # bar already exists, jut adjust coordinates
            self.canvasObj.coords(self.barObj[x], x0, y0, x1, y1)
            self.canvasObj.itemconfig(self.barObj[x], fill="yellow", outline="yellow")


        #
        #   Save y magnitude for resize event
        #   Save x0,x1 for beginning and end of every bar. This allows us to redraw the guide bars as the cw tuning bar is moved
        #
        self.barY[x] = y
        self.barX0[x] = x0
        self.barX1[x] = x1



    def drawHighLightBars(self, barPos):  #, scaleLength=1, scale=False ):
        #
        #   this calculation maps the scale (0-45) until the FFT Size (0-63)
        #   this allows us to draw two vertical lines that help target the apparent CW signal in the range
        #
        # if scale:
        #     barPos = round((x / scaleLength) * self.totalX)
        # else:
        #     barPos = x

        if self.barX0[barPos] == None: return

        x0 = self.barX0[barPos]
        x1 = self.barX1[barPos]

        if self.tuningLine1 == None:
            self.tuningLine1 = self.canvasObj.create_line(x0, self.canvas_height, x0, 0, fill="red", width=2, tags="tuningLine")
            self.tuningLine2 = self.canvasObj.create_line(x1,self.canvas_height,x1,0,fill="red", width=2, tags="tuningLine")
        else:

            self.canvasObj.coords(self.tuningLine1, x0, self.canvas_height, x0, 0)
            self.canvasObj.itemconfig(self.tuningLine1, fill="red")
            self.canvasObj.coords(self.tuningLine2, x1, self.canvas_height, x1, 0)
            self.canvasObj.itemconfig(self.tuningLine2, fill="red")

    def clearCanvas(self):
        print("clearCanvas")
        self.canvasObj.delete("bars")
        for x in range(self.totalX):
            self.barObj[x] = None

        if self.tuningLine1 != None:
            self.canvasObj.delete("tuningLing")
            self.tuningLine1 = None
            self.tuningLine2 = None


    def refreshCanvas(self):
        self.canvas_height = self.canvasObj.winfo_height()
        self.canvas_width = self.canvasObj.winfo_width()

        if self.barObj[0] == None:      # nothing has been plotted, can just return
            return
        #
        #   Recalculate Plot parameters
        #
        self.calculatePlotParameters()

        for x in range(self.totalX):
            self.drawBars(x,self.barY[x])


    #
    #   Setter/Getters
    #
    def set_CurrentMax (self, max):
        self.currentMax = max

    def get_CurrentMax(self):
        return(self.currentMax)


    def set_CurrentMin(self, min):
        self.currentMin = min

    def get_CurrentMin(self):
        return(self.currentMin)

