#!/usr/bin/python3
"""
Progress Warning Dialog

Just pops up a warning dialog

UI source file: progress_warning.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from delayWarning.delayWarning import delayWarning


#
# Builder definition section
#
widget_namespace = "delayWarning.delayWarning"
widget_classname = "delayWarning"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class delayWarningBO(BuilderObject):
    class_ = delayWarning

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, delayWarningBO, widget_classname, ("ttk", section_name)
)
