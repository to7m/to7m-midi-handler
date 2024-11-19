from abc import abstractmethod
from collections import namedtuple

from ...logging import log_err
from ...recursively_bindable import RecursivelyBindableBase


HandleSpecEntry = namedtuple("Entry", (item, msg_type_ints, binding_needed))


class HandleSpecBase(RecursivelyBindableBase):
    def __init__(self, *, receiver_name, from_str=''):
        self.receiver_name, self.from_str = receiver_name, from_str

        self.report_msg = self._make_report_msg()
        self.ignore_msg = lambda msg: None

        self._entries = []

    def _make_report_msg(self):
        err_str = (
            f"{receiver_name} received invalid message{from_str}:"
        )

        def report_msg(msg):
            log_err(err_str, msg)

        return report_msg

    def _get_bound_entries(self, bound_items):
        bound_items_iter = iter(bound_items)

        for item, msg_type_ints, binding_needed in self._entries:
            if binding_needed:
                yield next(bound_items_iter), msg_type_ints
            else:
                yield item, msg_type_ints

    def register_callback(
        self, callback, *msg_type_ints, binding_needed=False
    ):
        entry = HandleSpecEntry(callback, msg_type_ints, binding_needed)
        self._entries.append(entry)

    def callback_registrar_for(self, *msg_type_ints, binding_needed=False):
        def callback_registrar(callback):
            self.register_callback(
                callback, *msg_type_ints, binding_needed=binding_needed
            )

            return callback

        return callback_registrar

    def callback_method_registrar_for(self, *msg_type_ints):
        return self.callback_registrar_for(
            *msg_type_ints, binding_needed=True
        )

    def report(self, *msg_type_ints):
        self.register_callback(self.report_msg, *msg_type_ints)

    def ignore(self, *msg_type_ints):
        self.register_callback(self.ignore_msg, *msg_type_ints)

    def get_unbound_items(self):
        for item, msg_type_ints, binding_needed in self._entries:
            if binding_needed:
                yield item

    def get_bound(self, bound_items):
        bound_entries = list(self._get_bound_entries(bound_items))

        def handle(msg):
            bound_entries[msg.MSG_TYPE_INT](msg)

        return handle
