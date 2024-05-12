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

MIDI_CHANNEL = 16
KNOBS_OFFSET_CC = 1
STEPS_OFFSET_CC = 21
PADS_OFFSET_NOTE = 36


class BeatStepImpro(ControlSurface):
    knobs: List[EncoderElement]
    steps: List[ConfigurableButtonElement]
    pads: List[ConfigurableButtonElement]

    def __init__(self, c_instance):
        super(BeatStepImpro, self).__init__(c_instance)
        with self.component_guard():
            self.knobs = []
            self.steps = []
            self.pads = []

            self.setup_inputs();
            self.reset_knob_values_sysex();

    ################################################################################
    ## Control Inputs Setup

    def setup_inputs(self):
        self.setup_knobs();
        self.setup_steps();
        self.setup_pads();

    def setup_knobs(self):
        for midi_cc in range(KNOBS_OFFSET_CC, KNOBS_OFFSET_CC + 16):
            element = EncoderElement(MIDI_CC_TYPE, MIDI_CHANNEL - 1, midi_cc, Live.MidiMap.MapMode.absolute)
            element.add_value_listener(self.on_knob_input_value, identify_sender = True)
            self.knobs.append(element)

    def setup_steps(self):
        for midi_cc in range(STEPS_OFFSET_CC, STEPS_OFFSET_CC + 16):
            element = ConfigurableButtonElement(True, MIDI_CC_TYPE, MIDI_CHANNEL - 1, midi_cc)
            element.add_value_listener(self.on_step_input_value, identify_sender = True)
            self.steps.append(element)

    def setup_pads(self):
        for midi_note in range(PADS_OFFSET_NOTE, PADS_OFFSET_NOTE + 16):
            element = ConfigurableButtonElement(True, MIDI_NOTE_TYPE, MIDI_CHANNEL - 1, midi_note)
            element.add_value_listener(self.on_pad_input_value, identify_sender = True)
            self.pads.append(element)

    def on_knob_input_value(self, value: int, sender: EncoderElement):
        self.log_message(f"got knob input {value}, sender {sender}")

    def on_step_input_value(self, value: int, sender: ConfigurableButtonElement):
        self.log_message(f"got step input {value}, sender {sender}")

    def on_pad_input_value(self, value: int, sender: ConfigurableButtonElement):
        self.log_message(f"got pad input {value}, sender {sender}")

    ################################################################################
    ## SysEx

    def reset_knob_values_sysex(self):
        for position in range(0, 16):
            self.set_knob_value_sysex(position, 10)

    def set_knob_value_sysex(self, position: int, value: int):
        assert position >= 0 and position <= 15, "knob position must be between 0 and 15"
        clamped_value = min(max(value, 0), 127)
        sysex_message = bytes([0xf0, 0x00, 0x20, 0x6b, 0x7f, 0x42, 0x02, 0x00, 0x00, 0x20 + position, clamped_value, 0xf7])
        self._send_midi(sysex_message)

    def _send_sysex_and_wait(self, sysex_message: bytes, timeout: float = 1.0) -> bool:
        response = None
        self._send_midi(sysex_message)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._receive_midi(1) is not None:
                return True
        return False

    ################################################################################
    ## Release

    def disconnect(self):
        super(BeatStepImpro, self).disconnect()
