###################--------------TkDial-Jogwheel--------------###################
# URL = https://github.com/Akascape/TkDial/blob/main/tkdial/jogwheel.py
# Part of TKDial

import tkinter.ttk as ttk
import math

from Jogwheel import Jogwheel

class JogwheelCustom(Jogwheel):
    # jogwheel_num = 0    # used for debugging boundaries
    def __init__(self, master=None, **kw):


        self.foregroundColor={"normal":ttk.Style().lookup(master.cget('style'),'foreground'),
                              "disabled":ttk.Style().lookup(master.cget('style'),'background')
                              }
        self.textColor={    "normal":ttk.Style().lookup(master.cget('style'),'foreground'),
                            "disabled":"gray"
                              }
        self.buttonColor={  "normal":'yellow',
                            "disabled":"gray"
                              }

        self.scaleColor={"normal":'blue',
                         "disabled":"gray"
                         }


        self.initialValue = 0           # Provides default value on creation. Avoids requiring a set operation
        self.touchOptimized = False     # Provides alternative method for changing dial that is more
                                        # Optimized for touchscreens
        self.lastValue = 0              # lastValue saves the current value thru enable/disable operations
        self.angle_boundaries = {}  # Used to identify boundaries for touch zones
        self.last_segment = 0



        if "name" in kw:
            kw.pop("name")
        if "value" in kw:
            self.initialValue = kw.pop("value")
        if "touchOptimized" in kw:
            self.touchOptimized = kw.pop("touchOptimized")

        super().__init__(master,
                        bg=ttk.Style().lookup(master.cget('style'),'background'),
                        fg=ttk.Style().lookup(master.cget('style'),'background'),
                        text_font=ttk.Style().lookup(master.cget('style'),'font'),
                        **kw
        )

        if self.touchOptimized:
            self.create_touch_boundaries()          #touch boundaries only needed for Touchopttimized jogwheels

        self.lastValue = self.initialValue      #Set the initial value for the jogwheel
        self.set(self.lastValue)
        self.setStateDisabled()


    def setStateDisabled(self):
        self.configure(state="disabled", scroll=False)
        self.lastValue = self.get()
        self.configure( fg=self.foregroundColor["disabled"],
                        scale_color=self.scaleColor["disabled"],
                        button_color=self.buttonColor["disabled"],
                        text_color=self.textColor["disabled"]
                        )

    def setStateNormal(self):
        self.configure(state="normal", scroll=True)
        self.set(self.lastValue)
        self.configure( fg=self.foregroundColor["normal"],
                        scale_color=self.scaleColor["normal"],
                        button_color=self.buttonColor["normal"],
                        text_color=self.textColor["normal"]
                        )

    def create_touch_boundaries(self):
        lines = int( self.absolute)+1
        base_angle_degrees = ((360-abs(self.start_angle + self.end_angle)))/lines

        for i in range (lines):
            theAngle = (base_angle_degrees * (lines-i)) + self.start_angle    # -25
            bound1 = int(theAngle - (base_angle_degrees / 2))
            bound2 = int(theAngle + (base_angle_degrees / 2))
            if theAngle > 360:
                theAngle -= 360
            if bound1 > 360:
                bound1 -= 360
            if bound2 > 360:
                bound2 -= 360

            self.angle_boundaries[i] = [theAngle, bound1, bound2]
        # if JogwheelCustom.jogwheel_num == 0:
        #     print(self.start, self.max)
        #     print(self.start, self.max, self.angle_boundaries)
        #     print("lines", lines, "absolute", self.absolute, "start_angle", self.start_angle, "end_angle", self.end_angle)
        #     print("base_angle_degrees", base_angle_degrees)
        #     JogwheelCustom.jogwheel_num += 1

    def find_key_by_range(self, data_dict, target_value):
        for key, (center_angle, min_val, max_val) in data_dict.items():
            if min_val > max_val:
                if target_value >= min_val or target_value < max_val:
                    return key
            else:
                if min_val <= target_value < max_val:
                    return key

        return 0
#
    #
    # def on_circle_release(self, x, y, circle_center_x, circle_center_y):
    #     print("x y", x, y)
    #     newAngle = math.degrees(math.atan2(circle_center_y - y, x - circle_center_x))
    #     print("new angle =", newAngle)
    #     if newAngle < 0:
    #         print("in lower portion")
    #         print("real angle = ", abs(newAngle))
    #         angle = abs(newAngle)
    #     else:
    #         print("in upper portion")
    #         print("real angle = ", 360-abs(newAngle))
    #         angle = 360 - abs(newAngle)
    #
    #     result_key = self.find_key_by_range(self.angle_boundaries, angle)
    #     print("value =", result_key)
    #     return result_key



    def rotate_needle(self, event):
    #
    #     Causes the needle to rotate
    #
    #     # Get the coordinates of the mouse release event
        release_x, release_y = event.x, event.y
    #
    #   Since the center of x and y is an internal mangled protected instance variable, have tocreate the mangled name
    #   and then use getattr to get teh value
    #
        center_x = center_y = getattr(self,"_Jogwheel__x")
    #

        angle = math.degrees(math.atan2(center_y - event.y, event.x - center_x))

        if self.touchOptimized:
            if angle >0:
                # print("newangle =", angle, "prior angle=", self.previous_angle)
                self.set(self.find_key_by_range(self.angle_boundaries, angle))
            else:
                # print("negative newangle =", 360+angle, "prior angle=", self.previous_angle)
                self.set(self.find_key_by_range(self.angle_boundaries, 360 +angle))
        else:
            if self.previous_angle>angle:
                if self.max>self.start and self.start_angle>self.end_angle:
                    self.set(self.value+self.scroll_steps)
                elif self.max<self.start and self.start_angle<self.end_angle:
                    self.set(self.value+self.scroll_steps)
                else:
                    self.set(self.value-self.scroll_steps)
            else:
                if self.max>self.start and self.start_angle>self.end_angle:
                    self.set(self.value-self.scroll_steps)
                elif self.max<self.start and self.start_angle<self.end_angle:
                    self.set(self.value-self.scroll_steps)
                else:
                   self.set(self.value+self.scroll_steps)

        self.previous_angle = angle


    def configure(self, **kwargs):
        """
        This function contains some configurable options
        """

        if "text" in kwargs:
             self.itemconfigure(
                tagOrId="text",
                text=kwargs.pop("text"))

        if "start" in kwargs:
            self.start = kwargs.pop("start")

        if "end" in kwargs:
            self.end = kwargs.pop("end")

        if "bg" in kwargs:
            super().configure(bg=kwargs.pop("bg"))

        if "width" in kwargs:
            super().configure(width=kwargs.pop("width"))

        if "height" in kwargs:
            super().configure(height=kwargs.pop("height"))

        if "scale_color" in kwargs:
            self.itemconfigure(tagOrId="min_scale",
                    fill=kwargs['scale_color'])
            self.itemconfigure(
                tagOrId="progress",
                outline=kwargs.pop("scale_color"))

        if "fg" in kwargs:
            self.itemconfigure(
                tagOrId="face",
                fill=kwargs.pop('fg'))

        if "text_color" in kwargs:
            self.itemconfigure(
                tagOrId="text",
                fill=kwargs.pop("text_color"))

        if "button_color" in kwargs:
            self.itemconfigure(
                tagOrId="needle",
                fill=kwargs.pop("button_color"))

        if "border_color" in kwargs:
            self.itemconfigure(
                tagOrId="face",
                outline=kwargs.pop("border_color"))

        if "scroll_steps" in kwargs:
            self.scroll_steps = kwargs.pop("scroll_steps")

        if "scroll" in kwargs:
            if kwargs["scroll"]==False:
                super().unbind('<MouseWheel>')
                super().unbind('<Button-4>')
                super().unbind('<Button-5>')
            else:
                super().bind('<MouseWheel>', self.scroll_command)
                super().bind("<Button-4>", lambda e: self.scroll_command(-1))
                super().bind("<Button-5>", lambda e: self.scroll_command(1))
            kwargs.pop("scroll")

        if "integer" in kwargs:
            self.set(self.value)
            self.integer = kwargs.pop("integer")

        if "state" in kwargs:
            self.state = kwargs.pop("state")
            self.needle_state()
            if self.state == "normal":
                self.set(self.lastValue)
                self.configure(fg=self.foregroundColor["normal"],
                               scale_color=self.scaleColor["normal"],
                               button_color=self.buttonColor["normal"],
                               text_color=self.textColor["normal"]
                               )
            else:
                self.lastValue = self.get()
                self.configure(fg=self.foregroundColor["disabled"],
                               scale_color=self.scaleColor["disabled"],
                               button_color=self.buttonColor["disabled"],
                               text_color=self.textColor["disabled"]
                               )

        if "progress" in kwargs:
                self.progress = kwargs.pop("progress")

        if "command" in kwargs:
            self.command = kwargs.pop("command")

        if "touchOptimized" in kwargs:
            self.touchOptimized = kwargs.pop("touchOptimized")
            if self.touchOptimized:
                self.create_touch_boundaries()  # if jogwheel changes to touch_optimized must create boundaries

        if len(kwargs)>0:
            raise ValueError("unknown option: " + list(kwargs.keys())[0])

    def set (self, value, exceCommand=True):
        """
        This function is used to set the position of the needle
        """

        self.value = value
        angle = (value - self.start) * (self.end - self.start_angle) / (self.max - self.start) + self.start_angle

        if self.start < self.max:
            if value < self.start:
                self.value = self.start
                value = self.start
            elif value > self.max:
                self.value = self.max
                value = self.max
        else:
            if value > self.start:
                self.value = self.start
                value = self.start
            elif value < self.max:
                self.value = self.max
                value = self.max

        if self.progress:
            extend_angle = angle - (self.start_angle + self.end_angle)
            self.itemconfigure(self.arc_id, extent=extend_angle)

        self.coords(
            self.knob,
            self.line_coordinates(
                r1=0,
                r2=self.radius / 2 - self.arc_pos - self.bt_radius,
                angle=angle
            )
        )

        if self.integer == False:
            value = round(value, 2)
        else:
            value = int(value)

        if self.text:
            self.itemconfig(tagOrId='text', text=self.text + str(value), fill=self.text_color)

        if self.previous_angle != 0:
            if self.command is not None and exceCommand:
                self.command()