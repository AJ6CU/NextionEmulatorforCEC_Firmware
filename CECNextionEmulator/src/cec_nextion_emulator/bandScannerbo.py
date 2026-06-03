#!/usr/bin/python3
"""
Band Scanner

Scans up to three selected bands for signals.

UI source file: bandScanner.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.combobox import Combobox
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from bandScanner.bandScanner import bandScanner


#
# Builder definition section
#
widget_namespace = "bandScanner.bandScanner"
widget_classname = "bandScanner"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class bandScannerBO(BuilderObject):
    class_ = bandScanner

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, bandScannerBO, widget_classname, ("ttk", section_name)
)
