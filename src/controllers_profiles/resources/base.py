from threading import Thread
from queue import Queue

from ...logging import log_err, log_exceptions_and_restart
from ...connections_profiles_shared import ControllersProfileSpec


UNSORTED_CONTROLLERS_PROFILE_SPECS = []


class _ControllersProfileMeta(type):
    def __new__(cls, name, bases, namespace, is_base=False):
        inst = super().__new__(cls, name, bases, namespace)

        if not is_base:
            UNSORTED_CONTROLLERS_PROFILE_SPECS.append(
                ControllersProfileSpec(
                    priority=inst.PRIORITY,
                    connect_specs=inst.CONNECT_SPECS,
                    instantiator=inst.instantiator
                )
            )

        return inst


class ControllersProfileBase(metaclass=_ControllersProfileMeta, is_base=True):
    def __init__(self, sends):
        self._send_to_core = sends[0]

        self._handles_for_ports = list(self._get_handles_for_ports())

        self.ports_to_lcp_queue = Queue()

        Thread(target=self._run).start()

    def _get_handles_for_ports(self):
        for handle_spec in self.HANDLE_SPECS:
            if isinstance(
                handle_spec, HandleFromInternalSpec | HandleFromMidiSpec
            ):
                bound_methods = [
                    unbound_method.__get__(self, type(self))
                    for unbound_method in handle_spec.unbound_methods
                ]
                yield handle_spec.make_handle(bound_methods)
            else:
                log_err(
                    f"{type(self).__name__} does not recognise port type "
                    f"{type(port)}"
                )

    @log_exceptions_and_restart
    def _run(self):
        ports_to_lcp_queue_get = self.ports_to_lcp_queue.get
        handles_for_ports = self._handles_for_ports

        while True:
            port_i, msg = ports_to_lcp_queue_get()
            handles_for_ports[port_i](msg)

    @classmethod
    def instantiator(cls, sends):
        inst = cls(sends)
        return inst.ports_to_lcp_queue
