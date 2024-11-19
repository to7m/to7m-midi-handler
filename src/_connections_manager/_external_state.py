from ..to7m_aconnect import Aconnect


class RawExternalState:
    def __init__(self):
        self.aconnect = Aconnect.make_raw_output()

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return self.aconnect == other.aconnect


class ProcessedExternalState:
    def __init__(self, raw):
        self.aconnect = Aconnect.from_raw_output(raw.aconnect)
