from ..connections_profiles_shared import InternalConnectSpec, MidiConnectSpec


class ResourceClaimFailError(Exception):
    pass


class Resources:
    def __init__(self, midi_device_counts):
        self._midi_device_counts = midi_device_counts

    def _claim_midi(self, connect_spec):
        if connect_spec.aconnect_name not in self._midi_device_counts:
            raise ResourceClaimFailError

        if self._midi_device_counts[connect_spec.aconnect_name] < 1:
            raise ResourceClaimFailError

        self._midi_device_counts[connect_spec.aconnect_name] -= 1

    @classmethod
    def from_processed_external_state(cls, pes):
        return cls(midi_device_counts=pes.aconnect.get_device_counts())

    def copy(self):
        return Resources(self._midi_device_counts)

    def claim(self, connect_specs):
        for connect_spec in connect_specs:
            if isinstance(connect_spec, InternalConnectSpec):
                pass
            elif isinstance(connect_spec, MidiConnectSpec):
                self._claim_midi(connect_spec)
            else:
                log_err("unrecognised connect_spec type:", type(connect_spec))
