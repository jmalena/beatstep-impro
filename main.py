import Live # type: ignore
from _Framework.ControlSurface import ControlSurface # type: ignore
from _Framework.Layer import Layer # type: ignore
from _Framework.DeviceComponent import DeviceComponent # type: ignore
from _Framework.MixerComponent import MixerComponent # type: ignore
from _Framework.SliderElement import SliderElement # type: ignore
from _Framework.TransportComponent import TransportComponent # type: ignore
from _Framework.InputControlElement import * # type: ignore
from _Framework.ButtonElement import ButtonElement # type: ignore
from _Framework.ButtonMatrixElement import ButtonMatrixElement # type: ignore
from _Framework.SessionComponent import SessionComponent # type: ignore
from _Framework.EncoderElement import EncoderElement # type: ignore
from Launchpad.ConfigurableButtonElement import ConfigurableButtonElement # type: ignore
import time
from itertools import chain
from _Framework.Util import find_if # type: ignore
import collections
from typing import List

class BeatStepImpro(ControlSurface):
    knobs: List[EncoderElement]
    steps: List[ConfigurableButtonElement]
    pads: List[ConfigurableButtonElement]

    def __init__(self, c_instance):
        super(BeatStepImpro, self).__init__(c_instance)
        with self.component_guard():
            # TODO: move the config somewhere else
            self.midi_channel = 16
            self.knobs_offset_cc = 1;
            self.steps_offset_cc = 21;
            self.pads_offset_note = 36;
            self.led_off = 0 # FIXME: this is currently not supported on BSP
            self.led_on = 127 # FIXME: this is currently not supported on BSP

            self.knobs = []
            self.steps = []
            self.pads = []

            self.setup_inputs();

    def setup_inputs(self):
        self.setup_knobs();
        self.setup_steps();
        self.setup_pads();

    def setup_knobs(self):
        for midi_cc in range(self.knobs_offset_cc, self.steps_offset_cc + 16):
            element = EncoderElement(MIDI_CC_TYPE, self.midi_channel - 1, midi_cc, Live.MidiMap.MapMode.absolute)
            element.add_value_listener(self.on_knob_input_value, identify_sender = True)
            element.pre_val = 0 # FIXME: read actual value from BSP
            element.cur_val = 0 # FIXME: read actual value from BSP
            self.knobs.append(element)

    def setup_steps(self):
        for midi_cc in range(self.steps_offset_cc, self.steps_offset_cc + 16):
            element = ConfigurableButtonElement(True, MIDI_CC_TYPE, self.midi_channel - 1, midi_cc)
            element.set_on_off_values(self.led_on, self.led_off) # FIXME: this is currently not supported on BSP
            element.add_value_listener(self.on_step_input_value, identify_sender = True)
            element.pre_val = 0 # FIXME: read actual value from BSP
            element.cur_val = 0 # FIXME: read actual value from BSP
            self.steps.append(element)

    def setup_pads(self):
        for midi_note in range(self.pads_offset_note, self.pads_offset_note + 16):
            element = ConfigurableButtonElement(True, MIDI_NOTE_TYPE, self.midi_channel - 1, midi_note)
            element.set_on_off_values(self.led_on, self.led_off) # FIXME: this is currently not supported on BSP
            element.add_value_listener(self.on_pad_input_value, identify_sender = True)
            element.pre_val = 0 # FIXME: read actual value from BSP
            element.cur_val = 0 # FIXME: read actual value from BSP
            self.pads.append(element)

    def on_knob_input_value(self, value: int, sender: EncoderElement):
        self.log_message(f"got knob input {value}, sender {sender}")

    def on_step_input_value(self, value: int, sender: ConfigurableButtonElement):
        self.log_message(f"got step input {value}, sender {sender}")

    def on_pad_input_value(self, value: int, sender: ConfigurableButtonElement):
        self.log_message(f"got pad input {value}, sender {sender}")

    def disconnect(self):
        super(BeatStepImpro, self).disconnect()
