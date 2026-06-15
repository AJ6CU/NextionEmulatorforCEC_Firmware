#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import settingsMachineui as baseui
from configuration import configuration
import globalvars as gv
from VirtualNumericKeyboard import VirtualNumericKeyboard
from tkinter import messagebox
from entryFieldHandler import entryFieldHandler


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

        self.savePWR_SWR_Switch = gv.config.get_PWR_SWR_Switch()
        self.savePWR_Factor = gv.config.get_PWR_Factor()
        self.saveSWR_Factor = gv.config.get_SWR_Factor()

        self.PWR_Factor_Object = entryFieldHandler(self, "PWR_Factor", 3, VirtualNumericKeyboard, self.master)
        self.SWR_Factor_Object = entryFieldHandler(self, "SWR_Factor", 3, VirtualNumericKeyboard, self.master)


        self.saveMCU_Command_Headroom = int(gv.config.get_MCU_Command_Headroom()*1000)
        self.saveMCU_Update_Period = gv.config.get_MCU_Update_Period()
        self.saveMCU_Read_Wait_Period = gv.config.get_MCU_Read_Wait_Period()

        self.PWR_SWR_Enable_VAR.set(self.savePWR_SWR_Switch)

        if gv.config.get_NUMBER_DELIMITER() == ",":
            decimalDelim = "."
        else:
            decimalDelim = ","

        formatted_factor = self.savePWR_Factor.replace(".", decimalDelim)
        self.PWR_Factor_VAR.set(formatted_factor)

        formatted_factor = self.saveSWR_Factor.replace(".", decimalDelim)
        self.SWR_Factor_VAR.set(formatted_factor)

        if self.PWR_SWR_Enable_VAR.get() == 'False':
            self.disablePWR_SWR_CB()
        else:
            self.enablePWR_SWR_CB()




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
        self.popup.geometry(gv.POPUP_WINDOW_OFFSET)

        self.popup.wait_visibility()  # required on Linux
        self.popup.grab_set()
        self.popup.transient(self.mainWindow)

        self.pack(expand=tk.YES, fill=tk.BOTH)

    def selectDSP_On_CB(self):
        self.DSP_Enable_VAR.set('True')

    def selectDSP_Off_CB(self):
        self.DSP_Enable_VAR.set('False')

    def enablePWR_SWR_CB(self):
        self.PWR_SWR_Enable_VAR.set("True")
        self.PWR_Factor_Label.configure(state="normal")
        self.SWR_Factor_Label.configure(state="normal")
        self.PWR_Factor_Entry.configure(state="normal")
        self.SWR_Factor_Entry.configure(state="normal")

    def disablePWR_SWR_CB(self):
        self.PWR_SWR_Enable_VAR.set("False")
        self.PWR_Factor_Label.configure(state="disabled")
        self.SWR_Factor_Label.configure(state="disabled")
        self.PWR_Factor_Entry.configure(state="disabled")
        self.SWR_Factor_Entry.configure(state="disabled")

        #
        #   PWR Factor processing routines
        #

    def PWR_Factor_validation(self):
        std_float_str = self.PWR_Factor_VAR.get().replace(",","").replace(".", "")
        if 10.0 >= float(std_float_str)/10 >= 0.1:
                return True

        return False

    def PWR_Factor_errorHandler(self):
        # Bad factor entered, generate warning message and reset
        messagebox.showinfo("Error Illegal Factor",
                            "PWR Factor must be a number in the range of 0.1 to 10.0 \n\n Resetting to Prior value.",
                            parent=self)

    def PWR_Factor_preProcessor(self):
        return self.PWR_Factor_VAR.get().replace(",", "").replace(".", "")

    def PWR_Factor_postProcessor(self):
        factor = float(self.PWR_Factor_VAR.get())/10
        self.PWR_Factor_VAR.set(f"{factor:.1f}")


    def SWR_Factor_validation(self):
        std_float_str = self.SWR_Factor_VAR.get().replace(",","").replace(".", "")
        if 10.0 >= float(std_float_str)/10 >= 0.1:
                return True

        return False

    def SWR_Factor_errorHandler(self):
        # Bad factor entered, generate warning message and reset
        messagebox.showinfo("Error Illegal Factor",
                            "SWR Factor must be a number in the range of 0.1 to 10.0 \n\n Resetting to Prior value.",
                            parent=self)

    def SWR_Factor_preProcessor(self):
        return self.SWR_Factor_VAR.get().replace(",", "").replace(".", "")

    def SWR_Factor_postProcessor(self):
        factor = float(self.SWR_Factor_VAR.get())/10
        self.SWR_Factor_VAR.set(f"{factor:.1f}")


    def apply_CB(self):
        if self.DSP_Enable_VAR.get() != self.saveDSP_Enable:
            gv.config.set_DSP_Switch(self.DSP_Enable_VAR.get())
            self.mainWindow.theRadio.Set_DSP_State(self.DSP_Enable_VAR.get())

            if self.DSP_Enable_VAR.get() == "True":
                self.mainWindow.highlightCWorSpectrumBoxes(True)
            else:
                self.mainWindow.highlightCWorSpectrumBoxes(False)


        if self.PWR_SWR_Enable_VAR.get() != self.savePWR_SWR_Switch:
            gv.config.set_PWR_SWR_Switch(self.PWR_SWR_Enable_VAR.get())

        if self.PWR_Factor_Entry.get() != self.savePWR_Factor:
            formatted_factor = self.PWR_Factor_Entry.get().replace(",", ".")
            gv.config.set_PWR_Factor(formatted_factor)

        if self.SWR_Factor_Entry.get() != self.saveSWR_Factor:
            formatted_factor = self.SWR_Factor_Entry.get().replace(",", ".")
            gv.config.set_SWR_Factor(formatted_factor)


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
