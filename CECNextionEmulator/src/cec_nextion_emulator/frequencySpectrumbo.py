#!/usr/bin/python3
"""
Frequency Spectrum

Displays an area of the Frequency showing signal strength

UI source file: frequencySpectrum.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from frequencySpectrum import frequencySpectrum


#
# Builder definition section
#
widget_namespace = "frequencySpectrum"
widget_classname = "frequencySpectrum"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class frequencySpectrumBO(BuilderObject):
    class_ = frequencySpectrum

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, frequencySpectrumBO, widget_classname, ("ttk", section_name)
)
