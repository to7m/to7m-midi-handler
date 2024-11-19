class InternalConnectSpec:
    def __init__(self, *, handle_i, send_i):
        self.handle_i = handle_i
        self.send_i = send_i


class MidiConnectSpec:
    def __init__(self, *, aconnect_name, handle_indices, send_indices):
        self.aconnect_name = aconnect_name
        self.handle_indices = handle_indices
        self.send_indices = send_indices


class ControllersProfileSpec:
    def __init__(self, *, priority, connect_specs, instantiator):
        self.priority = priority
        self.connect_specs = connect_specs
        self.instantiator = instantiator
