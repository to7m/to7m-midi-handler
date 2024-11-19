from ._external_state import RawExternalState, ProcessedExternalState


class Scanner:
    def __init__(self):
        self._raw_external_state = None
        self._processed_external_state = None

    def scan(self):
        raw_external_state = RawExternalState()

        state_changed = raw_external_state != self._raw_external_state
        if state_changed:
            self._raw_external_state = raw_external_state
            self._processed_external_state = ProcessedExternalState(
                raw_external_state
            )

        return state_changed, self._processed_external_state
