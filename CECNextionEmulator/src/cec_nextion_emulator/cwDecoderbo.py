#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.api.v1 import (
    BuilderObject,
    register_widget,
)
from cwDecoder import cwDecoder


#
# Builder definition section
#

class cwDecoderBO(BuilderObject):
    class_ = cwDecoder


_builder_id = "projectcustom.cwDecoder"
register_widget(
    _builder_id, cwDecoderBO, "cwDecoder", ("ttk", "Project Widgets")
)
