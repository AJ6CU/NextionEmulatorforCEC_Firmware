#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from theVFO import theVFO


#
# Builder definition section
#
_widget_namespace = "theVFO"
_widget_classname = "theVFO"
_builder_namespace = "projectcustom"
_section_name = "Project Widgets"


class theVFOBO(BuilderObject):
    class_ = theVFO


_builder_id = f"{_builder_namespace}.{_widget_classname}"
register_widget(
    _builder_id, theVFOBO, _widget_classname, ("ttk", _section_name)
)
