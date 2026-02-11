import os
import tkinter.font as font
from tkinter import messagebox
import importlib.resources as pkg_resources

# from pygubu.plugins import ptk
import tkinter as tk
import pkgutil


#application required files################################################

def get_image(filename):
    image = pkgutil.get_data('cec_nextion_emulator', filename)

    if image is not None:
        return (tk.PhotoImage(data=image))

    else:
        imagepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
        return tk.PhotoImage(file=imagepath)

config = None
COMPORT = None

RELOADICON = "reloadicon.png"
BAUD = 9600
NUMBER_DELIMITER = ""               # Loaded with value from configuration file

MASTER_CAL_BOUNDS = {'LOW': -500000, 'HIGH': 500000}
BFO_CAL_BOUNDS = {'LOW': 11048000, 'HIGH': 12010000}
CW_CAL_BOUNDS = {'LOW': 11048000, 'HIGH': 12010000}
CW_TONE_BOUNDS = {'LOW':100, 'HIGH': 2000}
CW_SPEED_WPM_BOUNDS = {'LOW':1, 'HIGH': 250}
CW_START_TX_BOUNDS = {'LOW': 0, 'HIGH': 500}
CW_DELAY_Return_RX_BOUNDS = {'LOW': 0, 'HIGH': 2550}

FREQ_BOUNDS ={'LOW':0, 'HIGH':60000000}            # Min/Max for valid frequencies.

CW_KeyType = {  # 0: straight, 1 : iambica, 2: iambicb
    "0": "STRAIGHT",
    "1": "IAMBICA",
    "2": "IAMBICB"
}

CW_KeyValue = {
    "STRAIGHT": 0x0,
    "IAMBICA": 0x01,
    "IAMBICB": 0x02
}

CW_Sidetone_Values = ["100","200","250","300","350","400","425","450","475","500","525","550","575","600","625",
                      "650","675","700","725","750","775","800","850","900"]

CW_WPM_Values = ["1","5","8","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27",
                 "28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45"]

Start_TX_Values = ["0","10","25","50","75","100", "125", "150", "175", "200", "225","250","300","325","350","375","400",
                   "425","450","475","500"]

Delay_Return_RX_Values = ["0", "100","200","300","400","500","600","700","800","900","1000","1100","1200","1300","1400",
                          "1500", "1600", "1700","1800","1900","2000","2100","2200","2300","2400","2500"]

MCU_Headroom_Values = ["40","50","60","70","80","90","100","110","150","160","170","180","190","200"]

Frequency_To_Run_UX_loop = ["250","300","350","400","425","450","475","500","550","600","650","675","700","725","800"]


#   VFO Formatting Functions
#####################################################################################
### Start VFO Formatting Functions
#   These are methods are used to format the VFO with a delimiter (typically a period)
#   And to offset the VFO if we are in CW mode and the user has selected to see the TX freq
#####################################################################################

def formatVFO(VFO):
    global NUMBER_DELIMITER
    reversed_VFO = VFO[::-1]  # Reverse the string
    new_string_parts = []
    for i, char in enumerate(reversed_VFO):
        new_string_parts.append(char)
        # Insert the character after every 'n' characters, except at the very end
        if (i + 1) % 3 == 0 and (i + 1) != len(reversed_VFO):
            new_string_parts.append(NUMBER_DELIMITER)

    return "".join(new_string_parts[::-1])  # Join parts and reverse back

def updateNUMBER_DELIMITER(value):
    global NUMBER_DELIMITER
    NUMBER_DELIMITER = value


def formatFrequency(frequency, freqOffset=0):
    temp = str(int(frequency) + freqOffset)
    return formatVFO(temp)


def unformatFrequency(vfo, includeOffset=False, freqOffset=0):
    if includeOffset:
        return (vfo.replace(",", "").replace(".", ""))
    else:
        return (str(int(vfo.replace(",","").replace(".","")) - freqOffset))

def formatCombobox( combobox, family="Arial", size="36", weight="bold"):
    combobox.configure(font=font.Font(family=family, size=size, weight=weight))
    #
    #   The following is pure magic....  Found after hours of search. Basically the first command
    #   discovers the handle to the ListBox that is hidden below the combobox
    #   with this handle you can then set the drop down to the fonts used by the combobox.
    #   grab (create a new one or get existing) popdown
    popdown = combobox.tk.eval('ttk::combobox::PopdownWindow %s' % combobox)
    #   configure popdown font
    combobox.tk.call('%s.f.l' % popdown, 'configure', '-font', combobox['font'])

def validateNumber(value, lowbound, highbound, name, parent):
    if str(value) == "":
        messagebox.showinfo("Illegal Value for "+ name, "Source value for "+ name+ " is empty\n\nRequested change ignored", parent=parent)
        return False
    elif ((lowbound <= int(value)) & (highbound >= int(value))):
        return True
    else:
        messagebox.showinfo("Value for " + name+ " is out of range", "Source value (" + str(value) +") for "+ name+ " is not within "
                            + str(lowbound) +" to "+ str(highbound) +" \n\nRequested change ignored", parent=parent)
        return False

def validateKeyInDict(dict, key, name, parent):
    if key not in dict:
        messagebox.showinfo("Illegal Value for "+ key, "Source value (" + str(key) +") for "+ name+ " is not a valid option\n\nRequested change ignored", parent=parent)
        return False
    else:
        return True

def trimAndLocateWindow(window,x_offset,y_offset):
    window.update()        # Let things settle down so we can get

    width = window.winfo_width()
    height = window.winfo_height()

    return (f'{width}x{height}+{x_offset}+{y_offset}')

