from .bases import LcpToCoreUnserialisableMsgBase
from .lcp_to_core_serialisable import ()


"""
class RegisterHnrcDetailedMsg(LcpToCoreUnserialisableMsgBase):
    MSG_TYPE_INT = 10

    __slots__ = "hnrc_i", "vel_curve"

    def __init__(self, hnrc_i, vel_curve):
        self.hnrc_i = hnrc_i
        self.vel_curve = vel_curve

    def __iter__(self):
        return iter(())


class SetNotesRangeMsg(LcpToCoreUnserialisableMsgBase):
    hnrc_i, aps_i, notes_range


class LazyNoteOnWithVelMsg(LcpToCoreUnserialisableMsgBase):
    MSG_TYPE_INT = 11

    __slots__ = "hnrc_i", "src_midi_note", "src_vel", "hnrc_vel_curve"

    def __init__(
        self,
        hnrc_i, src_midi_note, src_vel,
        hnrc_vel_curve
    ):
        self.hnrc_i = hnrc_i
        self.src_midi_note = src_midi_note
        self.src_vel = src_vel
        self.hnrc_vel_curve = hnrc_vel_curve

    def __iter__(self):
        src_midi_note = self.src_midi_note
        true_vel = self.hnrc_vel_curve(src_midi_note)
        yield NoteOn(self.hnrc_i, src_midi_note, true_vel)



class SetDefaultTrueVelMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 6

    __slots__ = "pnrc_i", "true_vel"

    def __init__(self, pnrc_i, true_vel):
        self.pnrc_i = pnrc_i
        self.true_vel = true_vel


class NoteOnWithoutVelMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 7

    __slots__ = "hnrc_i", "src_midi_note"

    def __init__(self, hnrc_i, src_midi_note):
        self.hnrc_i = hnrc_i
        self.src_midi_note = src_midi_note
}
"""
