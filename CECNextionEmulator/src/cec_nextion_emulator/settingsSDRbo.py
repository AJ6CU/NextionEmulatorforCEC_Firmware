#!/usr/bin/python3
"""
settingsSDR

Used to save of machines

UI source file: settingsSDR.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.simpletooltip import Tooltip
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from settingsSDR import settingsSDR


#
# Builder definition section
#
widget_namespace = "settingsSDR"
widget_classname = "settingsSDR"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class settingsSDRBO(BuilderObject):
    class_ = settingsSDR

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, settingsSDRBO, widget_classname, ("ttk", section_name)
)
