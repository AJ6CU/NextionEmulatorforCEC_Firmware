#!/usr/bin/python3
"""
bandGraph

reuseable band graph object

UI source file: bandGraph.ui
"""
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from bandGraph import bandGraph


#
# Builder definition section
#
widget_namespace = "bandGraph"
widget_classname = "bandGraph"
builder_namespace = "custom_widgets"
section_name = "Project Widgets"


class bandGraphBO(BuilderObject):
    class_ = bandGraph

    def code_imports(self):
        # should return an iterable of (module, classname/function) to import
        # or None
        return [(widget_namespace, widget_classname)]


builder_id = f"{builder_namespace}.{widget_classname}"
register_widget(
    builder_id, bandGraphBO, widget_classname, ("ttk", section_name)
)
