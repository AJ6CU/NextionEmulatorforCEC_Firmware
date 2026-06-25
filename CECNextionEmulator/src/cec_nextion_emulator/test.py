#!/usr/bin/python3
"""
test

nonsense

UI source file: test.ui
"""
import pathlib
import tkinter as tk
import pygubu
from testui import testUI

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "test.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class test(testUI):
    def __init__(self, master=None):
        super().__init__(
            master,
            project_ui=PROJECT_UI,
            resource_paths=RESOURCE_PATHS,
            translator=None,
            on_first_object_cb=None
        )
        self.builder.connect_callbacks(self)


if __name__ == "__main__":
    root = tk.Tk()
    app = test(root)
    app.run()
