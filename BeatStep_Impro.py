import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonElement import ButtonElement
from typing import Callable, List
import time
from .utils import rescale

### Config ###

#### MIDI config #####
MIDI_CHANNEL = 16
KNOBS_MIDI_CC_MAP = range(1, 1 + 16)
STEPS_MIDI_CC_MAP = range(21, 21 + 16)
PADS_MIDI_CC_MAP = range(36, 36 + 16)

##### Tracks config #####
GROUP_NAME = "BeatStep Impro"
TRACK_NAMES = ["Sequencer 1", "Sequencer 2", "Drum", "FX"]

class BeatStep_Impro(ControlSurface):
    ### Control Inputs Setup ###
    knobs: List[EncoderElement]
    steps: List[ButtonElement]
    pads: List[ButtonElement]
    ### Tracks ###
    _tracks: List[Live.Track.Track]

    def __init__(self, c_instance):
        super(BeatStep_Impro, self).__init__(c_instance)
        with self.component_guard():
            ### Control Inputs Setup ###
            self.knobs = []
            self.steps = []
            self.pads = []
            ### Tracks ###
            self._tracks = [None] * len(TRACK_NAMES)

            if not self.find_tracks():
                self.log_warning(f"Either mandatory group {GROUP_NAME} is missing or any of it's tracks ({TRACK_NAMES}).")
                # FIXME: exit somehow here

            self.setup_control_inputs()

            ### Instruments Mapping ###
            _ = self.add_parameter_control_plugin(self.knobs[0], self._tracks[0], "Instrument Rack", "Instrument")
            _ = self.add_parameter_control_plugin(self.knobs[1], self._tracks[1], "Instrument Rack", "Instrument")
            _ = self.add_parameter_control_plugin(self.knobs[2], self._tracks[2], "Instrument Rack", "Instrument")

            ### Mixer Mapping ###
            _ = self.add_mixer_control_plugin(self.knobs[3], self._tracks[0])
            _ = self.add_mixer_control_plugin(self.knobs[4], self._tracks[1])
            _ = self.add_mixer_control_plugin(self.knobs[5], self._tracks[2])

            ### Sequencer 2 Mapping ###
            seq1_active = lambda: self.steps[0].is_pressed()
            _ = self.add_parameter_control_plugin(self.knobs[8], self._tracks[0], "Instrument Rack", "Cutoff", cond=seq1_active)
            _ = self.add_parameter_control_plugin(self.knobs[9], self._tracks[0], "Instrument Rack", "Resonance", cond=seq1_active)
            ### Sequencer 2 Mapping ###
            seq2_active = lambda: not self.steps[0].is_pressed()
            _ = self.add_parameter_control_plugin(self.knobs[8], self._tracks[1], "Instrument Rack", "Cutoff", cond=seq2_active)
            _ = self.add_parameter_control_plugin(self.knobs[9], self._tracks[1], "Instrument Rack", "Resonance", cond=seq2_active)
            ### Drum Mapping ###
            # TODO

            ### FX Mapping ###
            fx_active = lambda pad: lambda: pad.is_pressed()

            ##### EQ Mapping #####
            _ = self.add_parameter_control_plugin(self.knobs[14], self._tracks[3], "Audio Effect Rack", "EQ LP", cond=fx_active(self.pads[13]))
            _ = self.add_parameter_control_plugin(self.knobs[15], self._tracks[3], "Audio Effect Rack", "EQ HP", cond=fx_active(self.pads[13]))

            ##### Compressor Mapping #####
            # TODO

            ##### Reverb Mapping #####
            _ = self.add_parameter_control_plugin(self.knobs[14], self._tracks[3], "Audio Effect Rack", "Reverb Level", cond=fx_active(self.pads[14]))
            _ = self.add_parameter_control_plugin(self.knobs[15], self._tracks[3], "Audio Effect Rack", "Reverb Feedback", cond=fx_active(self.pads[14]))

            ##### Delay Mapping #####
            _ = self.add_parameter_control_plugin(self.knobs[14], self._tracks[3], "Audio Effect Rack", "Delay Level", cond=fx_active(self.pads[6]))
            _ = self.add_parameter_control_plugin(self.knobs[15], self._tracks[3], "Audio Effect Rack", "Delay Feedback", cond=fx_active(self.pads[6]))


    ################################################################################
    ## Control Inputs Setup
    ################################################################################

    def setup_control_inputs(self):
        self._setup_control_knobs()
        self._setup_control_steps()
        self._setup_control_pads()

    def _setup_control_knobs(self):
        for midi_cc in KNOBS_MIDI_CC_MAP:
            element = EncoderElement(MIDI_CC_TYPE, MIDI_CHANNEL - 1, midi_cc, Live.MidiMap.MapMode.absolute)
            element.add_value_listener(self._on_control_knob_value, identify_sender = True)
            self.knobs.append(element)

    def _setup_control_steps(self):
        for midi_cc in STEPS_MIDI_CC_MAP:
            element = ButtonElement(True, MIDI_CC_TYPE, MIDI_CHANNEL - 1, midi_cc)
            element.add_value_listener(self._on_control_step_value, identify_sender = True)
            self.steps.append(element)

    def _setup_control_pads(self):
        for midi_cc in PADS_MIDI_CC_MAP:
            element = ButtonElement(True, MIDI_CC_TYPE, MIDI_CHANNEL - 1, midi_cc)
            element.add_value_listener(self._on_control_pad_value, identify_sender = True)
            self.pads.append(element)

    def _on_control_knob_value(self, value: int, sender: EncoderElement):
        """
        NOTE: Just for the debugging purposes.
        """
        self.log_message(f"Received control knob input {value} from {sender.message_identifier()}")

    def _on_control_step_value(self, value: int, sender: ButtonElement):
        """
        NOTE: Just for the debugging purposes.
        """
        self.log_message(f"Received control step input {value} from {sender.message_identifier()}")

    def _on_control_pad_value(self, value: int, sender: ButtonElement):
        """
        NOTE: Just for the debugging purposes.
        """
        self.log_message(f"Received control pad input {value} from {sender.message_identifier()}")

    ###############################################################################
    ## Tracks
    ################################################################################

    def find_tracks(self) -> bool:
        for track in self.song().tracks:
            if track.is_grouped and track.group_track.name == GROUP_NAME and track.name in TRACK_NAMES:
                idx = TRACK_NAMES.index(track.name)
                self._tracks[idx] = track
        return None not in self._tracks

    ################################################################################
    ## SysEx
    ################################################################################

    def set_knob_value_sysex(self, index: int, value: int):
        """
        TODO: move to custom EncoderElement class in future
        FIXME: seems to not work anymore
        """
        assert index >= 0 and index <= 15, "Knob index must be between 0 and 15."
        clamped_value = min(max(value, 0), 127)
        sysex_message = bytes([0xf0, 0x00, 0x20, 0x6b, 0x7f, 0x42, 0x02, 0x00, 0x00, 0x20 + index, clamped_value, 0xf7])
        self._send_midi(sysex_message)

    def _send_sysex_and_wait(self, sysex_message: bytes, timeout: float = 1.0) -> bool:
        self._send_midi(sysex_message)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._receive_midi(1) is not None:
                return True
        return False

    ################################################################################
    #### Parameter Control Plugin
    ################################################################################
    def add_parameter_control_plugin(self, knob: EncoderElement, track: Live.Track.Track, device_name: str, parameter_name: str, cond: Callable[[], bool] = lambda: True) -> Callable[[], None]:
        param = self._find_track_parameter(track, device_name, parameter_name)

        if not param:
            self.log_warning(f"Parameter \"{parameter_name}\" for track \"{track.name}\" wasn't found in the device \"{device_name}\"")
            return lambda: None

        def on_knob_value_change(value: int):
            if cond():
                param.value = value

        knob.add_value_listener(on_knob_value_change)
        return lambda: knob.remove_value_listener(on_knob_value_change)

    def _find_track_parameter(self, track: Live.Track.Track, device_name: str, paramter_name: str) -> Live.DeviceParameter.DeviceParameter:
        """
        Returns first occurence of a paramter within a track's device
        """
        for device in track.devices:
            if device.name == device_name:
                 for parameter in device.parameters:
                     if parameter.name == paramter_name:
                         return parameter

        return None


    ################################################################################
    #### Mixer Control Plugin
    ################################################################################

    def add_mixer_control_plugin(self, knob: EncoderElement, track: Live.Track.Track) -> Callable[[], None]:
        def on_knob_value_change(value: int):
            next_volume = rescale(0, 127, 0.0, 1.0, value)
            track.mixer_device.volume.value = next_volume

        knob.add_value_listener(on_knob_value_change)
        return lambda: knob.remove_value_listener(on_knob_value_change)


    ################################################################################
    ## Logging
    ################################################################################

    def log_warning(self, msg: str):
        self.log_message(f"[warning] {msg}")

    ################################################################################
    ## Release
    ################################################################################

    def disconnect(self):
        super(BeatStep_Impro, self).disconnect()


