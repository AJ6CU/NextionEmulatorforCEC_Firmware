#!/usr/bin/python3
"""
settingsAbout

Used to save general settings

UI source file: settingsAbout.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from settingsAbout import settingsAbout


#
# Builder definition section
#
widget_namespace = "settingsAbout"
widget_classname = "settingsAbout"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class settingsAboutBO(BuilderObject):
    class_ = settingsAbout

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, settingsAboutBO, widget_classname, ("ttk", section_name)
)
