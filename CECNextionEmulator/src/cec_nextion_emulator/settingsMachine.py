#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import settingsMachineui as baseui
from configuration import configuration
import globalvars as gv


#
# Manual user code
#

class settingsMachine(baseui.settingsMachineUI):
    def __init__(self, master=None, mainWindow=None, **kw):
        self.master = master
        self.mainWindow = mainWindow
        #
        #   Create a toplevel window to contain the settings popup
        #
        self.popup = tk.Toplevel(self.master)

        super().__init__(self.popup, **kw)

        self.MCU_Command_Headroom_Spinbox.configure(values=gv.MCU_Headroom_Values)
        self.MCU_Update_Period_Spinbox.configure(values=gv.Frequency_To_Run_UX_loop)
        self.MCU_Read_Wait_Period_Spinbox.configure(values=gv.MCU_Read_Completion_Wait_Period)


        self.saveDSP_Enable = gv.config.get_DSP_Switch()
        self.saveMCU_Command_Headroom = int(gv.config.get_MCU_Command_Headroom()*1000)
        self.saveMCU_Update_Period = gv.config.get_MCU_Update_Period()
        self.saveMCU_Read_Wait_Period = gv.config.get_MCU_Read_Wait_Period()

        self.DSP_Enable_VAR.set(self.saveDSP_Enable)
        self.MCU_Command_Headroom_VAR.set(str(self.saveMCU_Command_Headroom))
        self.MCU_Update_Period_VAR.set(str(self.saveMCU_Update_Period))
        self.MCU_Read_Wait_Period_VAR.set(str(int(self.saveMCU_Read_Wait_Period*1000)))


        if self.mainWindow.DSPFound:
            self.DSP_Enable_Label.configure(state="normal")
            self.DSP_Enable_Menubutton.configure(state="normal")
            self.DSPMessage_VAR.set("")
        else:
            self.DSP_Enable_Label.configure(state="disabled")
            self.DSP_Enable_Menubutton.configure(state="disabled")
            self.DSPMessage_VAR.set("No DSP Found on startup. Option automatically disabled")

        #
        #   Can now kickoff the UX
        #

        self.initUX()

    def initUX(self):
        self.popup.title("Machine Settings - Advanced Usage Only")

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)
        gv.trimAndLocateWindow(self.popup, 0, 0)

    def selectDSP_On_CB(self):
        self.DSP_Enable_VAR.set('True')

    def selectDSP_Off_CB(self):
        self.DSP_Enable_VAR.set('False')

    def apply_CB(self):
        print("Applying settings")
        print("current dsp switch is", self.DSP_Enable_VAR.get())
        if self.DSP_Enable_VAR.get() != self.saveDSP_Enable:
            gv.config.set_DSP_Switch(self.DSP_Enable_VAR.get())
            print('changing DSP_Switch, new setting is', gv.config.get_DSP_Switch(), self.DSP_Enable_VAR.get())
            self.mainWindow.theRadio.Set_DSP_State(self.DSP_Enable_VAR.get())

            if self.DSP_Enable_VAR.get() == "True":
                self.mainWindow.highlightCWorSpectrumBoxes(True)
            else:
                self.mainWindow.highlightCWorSpectrumBoxes(False)

        if int(self.MCU_Command_Headroom_VAR.get()) != self.saveMCU_Command_Headroom:
            gv.config.set_MCU_Command_Headroom(int(self.MCU_Command_Headroom_VAR.get())/1000)


        if int(self.MCU_Update_Period_VAR.get()) != self.saveMCU_Update_Period:
            gv.config.set_MCU_Update_Period(int(self.MCU_Update_Period_VAR.get()))

        if int(self.MCU_Read_Wait_Period_VAR.get()) != self.saveMCU_Read_Wait_Period:
            gv.config.set_MCU_Read_Wait_Period(int(self.MCU_Read_Wait_Period_VAR.get())/1000)

        self.master.destroy()

    def cancel_CB(self):
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    widget = settingsMachine(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
