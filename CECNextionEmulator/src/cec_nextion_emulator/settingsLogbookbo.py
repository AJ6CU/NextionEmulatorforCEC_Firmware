#!/usr/bin/python3
"""
settingsLogbook

Manages the settings for the logbook function

UI source file: settingsLogbook.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from settingsLogbook import settingsLogbook


#
# Builder definition section
#
widget_namespace = "settingsLogbook"
widget_classname = "settingsLogbook"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class settingsLogbookBO(BuilderObject):
    class_ = settingsLogbook

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, settingsLogbookBO, widget_classname, ("ttk", section_name)
)
