#!/usr/bin/python3
"""
sdrDashboard

A small window that pops up when a sdr is connected

UI source file: sdrDashboard.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from sdrDashboard import sdrDashboard


#
# Builder definition section
#
widget_namespace = "sdrDashboard"
widget_classname = "sdrDashboard"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class sdrDashboardBO(BuilderObject):
    class_ = sdrDashboard

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, sdrDashboardBO, widget_classname, ("ttk", section_name)
)
