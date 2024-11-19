from ..connections_profiles_shared import InternalConnectSpec, MidiConnectSpec
from ..tmh_msgs import (
    RegisterPatchesSlotMsg, DeregisterPatchesSlotMsg, NoteOnMsg
)
from ..curves import 
from .resources import (
    ControllersProfileBase, HandleInternalSpec, HandleMidiSpec
)


def _make_vel_curve():
    vel_curve_factory = MidiToTrueVelCurveFactory()
    vel_curve_factory.add_pair_for_all_notes(1, 0.0)
    vel_curve_factory.add_pair_for_all_notes(2, 0.3)
    vel_curve_factory.add_pair_for_all_notes(127, 0.8)
    vel_curve = vel_curve_factory()


vel_curve = _make_vel_curve()


class TmpExampleControllersProfile(ControllersProfileBase):
    PRIORITY = 0

    HANDLE_SPECS = [
        HandleInternalSpec("TmpExampleControllersProfile", port_i=0),
        HandleMidiSpec("TmpExampleControllersProfile", port_i=1),
        HandleMidiSpec("TmpExampleControllersProfile", port_i=2)
    ]

    CONNECT_SPECS = [
        InternalConnectSpec(handle_i=0, send_i=0),
        MidiConnectSpec(
            aconnect_name="ExampleKeyboardName",
            handle_indices=[1, 2],
            send_indices=[1, 2]
        ),
        MidiConnectSpec(
            aconnect_name="KeytarName",
            handle_indices=[3, None],
            send_indices=[None, None]
        )
    ]

    def __init__(self, sends):
        super().__init__(sends)

        self._send_to_core(RegisterPatchesSlotMsg(0))

    @HANDLE_SPECS[1].callback_method_registrar_for([144])
    def handle_note_on(self, msg):
        _, midi_note, midi_vel = msg

        self._send_to_core(
            NoteOnMsg(0, midi_note, vel_curve(midi_note, midi_vel))
        )

    HANDLE_SPECS[1].ignore([144, 60])
    HANDLE_SPECS[1].report([144, 61])
