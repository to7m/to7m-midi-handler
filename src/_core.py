from queue import Queue

from .logging import log_exceptions_and_restart
from .error import To7mMidiHandlerError
from ._handlers import Bindable, HandleSpecBase
from ._connections import ConnectionsManager
from ._recordings import RecordingsManager, RecordingsManagerDummyQueue


class CoreInternalError(To7mMidiHandlerError):
    pass


class _GlobalState:
    def __init__(self):
        self.pitched_transposition_st = 0


class _PatchesSlotState:
    def __init__(self):
        self.pitch_bend_st = 0.0
        self.precurved_vol = 0.5
        self.param_a = 0.5
        self.param_b = 0.5
        self.param_c = 0.5
        self.param_d = 0.5


class _LcpManager:
    def __init__(self, to_lcp_queue):
        self.to_lcp_queue = to_lcp_queue

        self.patches_slot_states = []


class TmhCore:
    HANDLE_SPEC = HandleToCoreSpec()

    HANDLE_CONNECTIONS_MANAGER_TO_CORE_SPEC \
        = HandleConnectionsManagerToCoreSpec()
    HANDLE_SPEC.register_callback(
        HANDLE_CONNECTIONS_MANAGER_TO_CORE_SPEC,
        ConnectionsManagerToCoreMsg.MSG_TYPE_INT,
        binding_needed=True
    )

    HANDLE_LCP_TO_CORE_GLOBAL_SPEC \
        = HandleLcpToCoreGlobalSpec()
    HANDLE_SPEC.register_callback(
        HANDLE_LCP_TO_CORE_GLOBAL_SPEC,
        LcpToCoreGlobalMsg.MSG_TYPE_INT,
        binding_needed=True
    )

    HANDLE_LCP_TO_CORE_PSLOT_SPEC \
        = HandleLcpToCorePslotSpec()
    HANDLE_SPEC.register_callback(
        HANDLE_LCP_TO_CORE_PSLOT_SPEC,
        LcpToCorePslotMsg.MSG_TYPE_INT,
        binding_needed=True
    )

    HANDLE_LCP_TO_CORE_RECORDINGS_MANAGER_SPEC \
        = HandleLcpToCoreRecordingsManagerSpec()
    HANDLE_SPEC.register_callback(
        HANDLE_LCP_TO_CORE_RECORDINGS_MANAGER_SPEC,
        LcpToCoreRecordingsManagerMsg.MSG_TYPE_INT,
        binding_needed=True
    )

    def __init__(
        self, controllers_profiles_specs, sound_modules_profiles_specs
    ):
        self.queue = Queue()
        self._handle = self._bind(HANDLE_TO_CORE_SPEC)

        self._connections_manager = ConnectionsManager(
            controllers_profiles_specs, sound_modules_profiles_specs,
            to_core_queue=self._to_core_queue
        )

        self._lcp_managers = [_LcpManager(RecordingsManagerDummyQueue())]
        self.to_lsmp_queues = []

    def _bind(self, bindable):
        if isinstance(bindable, RecursivelyBindableBase):
            bound_items = [
                self._bind(unbound_item)
                for unbound_item in bindable.get_unbound_items()
            ]

            if isinstance(bindable, HandleLcpToCoreBase):
                return bindable.get_bound(
                    bound_items, self._recordings_manager.queue
                )
            else:
                return bindable.get_bound(bound_items)
        else:
            return bindable.__get__(self, type(self))

    def _get_global_state_msg(self):
        +...
        return

    def _get_lcp_state_msgs(self):
        +...
        yield

    @HANDLE_LCP_TO_CORE_GLOBAL_SPEC.callback_method_registrar_for(
        SetGlobalPitchedTranspositionMsg.MSG_TYPE_INT
    )
    def handle_set_global_pitched_transposition(self, msg):
        msg.lcp_to_core_msg
        +...

    @HANDLE_LCP_TO_CORE_RECORDINGS_MANAGER_SPEC.callback_method_registrar_for(
        StartRecordingMsg.MSG_TYPE_INT
    )
    def handle_start_recording(self, msg):
        global_state_msg = self._get_global_state_msg()
        self._recordings_manager.queue.put(global_state_msg)

        for lcp_state_msg in self._get_lcp_state_msgs():
            self._recordings_manager_queue.put(lcp_state_msg)

    HANDLE_LCP_TO_CORE_RECORDINGS_MANAGER_SPEC.ignore(
        StopRecordingMsg.MSG_TYPE_INT,
        StartPlaybackMsg.MSG_TYPE_INT,
        StopPlaybackMsg.MSG_TYPE_INT
    )

    def run(self):
        queue_get = self.queue.get
        handle = self._handle

        with self._connections_manager:
            while True:
                handle(queue_get())
