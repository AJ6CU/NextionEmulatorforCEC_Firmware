import tkinter as tk


from pygubu.api.v1 import (
    BuilderObject,
    register_widget, register_custom_property,
)
from JogwheelCustom import JogwheelCustom

#
# Builder definition section
#

class JogwheelCustom_UXbo(BuilderObject):
    class_ = JogwheelCustom
    OPTIONS_CUSTOM = {
        "start",
        "end",
        "divisions",
        "value",
        "scroll_steps",
        "scroll",
        "radius",
        "button_radius",
        "command",
        "progress",
        "state",
        "touchOptimized"
    }
    ro_properties = ("start", "end", "divisions", "radius", "button_radius", "value", "progress", "scroll", "scroll_steps")
    command_properties = ("command",)
    properties = OPTIONS_CUSTOM

    virtual_events = ("<<JogwheelCustomSelected>>",)
    # def _code_set_property(self, targetid, pname, value, code_bag):
    #     if pname == "command":
    #         code_bag[pname] = f"{targetid}.{value})"
    #     else:
    #         super(JogwheelCustom_UXbo, self)._code_set_property(
    #             targetid, pname, value, code_bag
    #         )

    def _process_property_value(self, pname,value):
        if pname in ("start", "end", "divisions", "value", "scroll_steps", "radius", "button_radius"):
            return int(value)
        return super()._process_property_value(pname,value)


_builder_id = "projectcustom.Jogwheel"
register_widget(
    _builder_id, JogwheelCustom_UXbo, "Jogwheel", ("tk", "Project Widgets")
)



register_custom_property (
    _builder_id,
    "start",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "end",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "divisions",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "value",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "radius",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "button_radius",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "scroll_steps",
    "integernumber"
)

register_custom_property (
    _builder_id,
    "scroll",
    "choice",
    values=("True", "False")
)

register_custom_property (
    _builder_id,
    "progress",
    "choice",
    values=("True", "False")
)

register_custom_property (
    _builder_id,
    "state",
    "choice",
    values=("normal", "disabled")
)

register_custom_property (
    _builder_id,
    "command",
    "commandentry"
)


register_custom_property (
    _builder_id,
    "touchOptimized",
    "choice",
    values=("True", "False")
)