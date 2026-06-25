#!/usr/bin/python3
"""
test

nonsense

UI source file: test.ui
"""
import tkinter as tk
from pygubu.widgets.accordionframe import AccordionFrame



def safe_i18n_translator(value):
    """i18n - Setup translator in derived class file"""
    return value


def safe_fo_callback(widget):
    """on first objec callback - Setup callback in derived class file."""
    pass


def safe_image_loader(master, image_name: str):
    """Image loader - Setup image_loader in derived class file."""
    img = None
    try:
        img = tk.PhotoImage(file=image_name, master=master)
    except tk.TclError:
        pass
    return img


class testUI:


    def __init__(
        self,
        master=None,
        *,
        translator=None,
        on_first_object_cb=None,
        data_pool=None,
        image_loader=None
    ):
        if translator is None:
            translator = safe_i18n_translator
        _ = translator  # i18n string marker.
        if image_loader is None:
            image_loader = safe_image_loader
        if on_first_object_cb is None:
            on_first_object_cb = safe_fo_callback
        # build ui
        self.accordionframe1 = AccordionFrame(master)

        # First object created
        on_first_object_cb(self.accordionframe1)

        accordionframegroup1 = self.ClassNameNotDefined('accordionframegroup1')

        accordionframegroup2 = self.ClassNameNotDefined('accordionframegroup2')

        accordionframegroup3 = self.ClassNameNotDefined('accordionframegroup3')

        self.accordionframe1.pack(side="top")

        # Main widget
        self.mainwindow = self.accordionframe1

    def run(self):
        self.mainwindow.mainloop()

    def ClassNameNotDefined(self, name):
        return (self.accordionframe1.add_group('g1', name))


if __name__ == "__main__":
    root = tk.Tk()
    app = testUI(root)
    app.run()
