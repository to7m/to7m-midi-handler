from .bases import LcpToCoreSerialisableMsgBase


class SetGlobalPitchedTranspositionMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 0

    __slots__ = "semitones_up"

    def __init__(self, semitones_up):
        self.semitones_up = semitones_up


class RegisterPatchesSlotMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 1

    __slots__ = "patches_slot_i",

    def __init__(self, patches_slot_i):
        self.patches_slot_i = patches_slot_i


class DeregisterPatchesSlotMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 2

    __slots__ = "patches_slot_i",

    def __init__(self, patches_slot_i):
        self.patches_slot_i = patches_slot_i


class NoteOnMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 3

    __slots__ = "patches_slot_i", "midi_note", "true_vel"

    def __init__(self, patches_slot_i, midi_note, true_vel):
        self.patches_slot_i = patches_slot_i
        self.midi_note = midi_note
        self.true_vel = true_vel


class NoteOffMsg(LcpToCoreSerialisableMsgBase):
    MSG_TYPE_INT = 4

    __slots__ = "patches_slot_i", "midi_note"

    def __init__(self, patches_slot_i, midi_note):
        self.patches_slot_i = patches_slot_i
        self.midi_note = midi_note
