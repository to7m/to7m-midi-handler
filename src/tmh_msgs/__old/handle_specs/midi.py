from collections import namedtuple

from ._base import HandleSpecBase


_CallbackEntry = namedtuple(
    "_CallbackEntry", ("callback", "msg_starts", "binding_needed")
)


class _CallbackFactory:
    def __init__(self, callback):
        self._data = callback

    def __call__(self, msg_index):
        if type(self._data) is list:
            callback_factories = self._data

            callbacks = [
                callback_factory(msg_index + 1)
                for callback_factory in callback_factories
            ]

            def callback(msg):
                callbacks[msg[msg_index]](msg)
        else:
            callback = self._data

        return callback

    def register_callback(self, callback, msg_start_remainder):
        if msg_start_remainder:
            next_byte, *msg_start_remainder = msg_start_remainder

            if type(self._data) is list:
                callback_factories = self._data
            else:
                old_callback = self._data
                self._data = callback_factories = [
                    _CallbackFactory(old_callback) for _ in range(256)
                ]

            callback_factories[next_byte].register_callback(
                callback, msg_start_remainder
            )
        else:
            self._data = callback


class HandleMidiSpec(HandleSpecBase):
    def __init__(self, controllers_profile_name, *, port_i):
        super().__init__(controllers_profile_name, port_i=port_i)

        self._callback_entries, self.unbound_methods = [], []

    def _get_msg_starts_and_callbacks(self, bound_methods):
        bound_methods_iter = iter(bound_methods)

        for entry in self._callback_entries:
            if entry.binding_needed:
                callback = next(bound_methods_iter)
            else:
                callback = entry.callback

            for msg_start in entry.msg_starts:
                yield msg_start, callback

    def register_callback(self, callback, *msg_starts, binding_needed=False):
        entry = _CallbackEntry(callback, msg_starts, binding_needed)
        self._callback_entries.append(entry)

        if binding_needed:
            self.unbound_methods.append(callback)

    def callback_registrar_for(self, *msg_starts, binding_needed=False):
        def callback_registrar(callback):
            self.register_callback(
                callback, *msg_starts, binding_needed=binding_needed
            )

            return callback

        return callback_registrar

    def callback_method_registrar_for(self, *msg_starts):
        return self.callback_registrar_for(*msg_starts, binding_needed=True)

    def report(self, *msg_starts):
        self.register_callback(self.report_msg, *msg_starts)

    def ignore(self, *msg_starts):
        self.register_callback(self.ignore_msg, *msg_starts)

    def make_handle(self, bound_methods):
        callback_factory = _CallbackFactory(self.report_msg, [])

        for msg_start, callback in self._get_msg_starts_and_callbacks():
            callback_factory.register_callback(
                callback, msg_start_remainder=msg_start
            )

        return callback_factory(msg_index=0)
