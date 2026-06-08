#!/usr/bin/python3
"""
Log QSO

Completes the logging of a QSO

UI source file: logQSO.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from logQSO import logQSO


#
# Builder definition section
#
widget_namespace = "logQSO"
widget_classname = "logQSO"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class logQSOBO(BuilderObject):
    class_ = logQSO

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, logQSOBO, widget_classname, ("ttk", section_name)
)
