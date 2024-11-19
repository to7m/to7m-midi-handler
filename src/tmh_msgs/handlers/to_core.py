from time import monotonic_ns

from .base import HandleSpecBase


class HandleToCoreSpec(HandleSpecBase):
    def __init__(self):
        super().__init__(receiver_name="TmhCore instance")


class HandleConnectionsManagerToCoreSpec(HandleSpecBase):
    def __init__(self):
        super().__init__(
            receiver_name="TmhCore instance",
            from_str=" from ConnectionsManager instance"
        )

    def get_bound(self, bound_items):
        bound_entries = list(self._get_bound_entries(bound_items))

        def handle(msg):
            nested = msg.nested
            bound_entries[nested.MSG_TYPE_INT](nested)

        return handle


class HandleLcpToCoreBase(HandleSpecBase):
    pass


class HandleLcpToCoreGlobalSpec(HandleLcpToCoreBase):
    def __init__(self):
        super().__init__(
            receiver_name="TmhCore instance", from_str=" from LCP"
        )

    def get_bound(self, bound_items, to_recordings_manager_queue):
        bound_entries = list(self._get_bound_entries(bound_items))

        def handle(msg):
            timestamp_ns = monotonic_ns()
            nested = msg.nested
            bound_entries[nested.MSG_TYPE_INT](nested)
            to_recordings_manager_queue.put(
                TimestampedLcpToCoreGlobalMsg(timestamp_ns, nested)
            )

        return handle


class HandleLcpToCorePslotSpec(HandleLcpToCoreBase):
    def __init__(self):
        super().__init__(
            receiver_name="TmhCore instance", from_str=" from LCP"
        )

    def get_bound(self, bound_items, to_recordings_manager_queue):
        bound_entries = list(self._get_bound_entries(bound_items))

        def handle(msg):
            timestamp_ns = monotonic_ns()
            nested = msg.nested
            bound_entries[nested.MSG_TYPE_INT](msg.lcp_i, nested)
            to_recordings_manager_queue.put(
                TimestampedLcpToCorePslotMsg(timestamp_ns, msg.lcp_i, nested)
            )

        return handle


class HandleLcpToCoreRecordingsManagerSpec(HandleLcpToCoreBase):
    def __init__(self):
        super().__init__(
            receiver_name="TmhCore instance", from_str=" from LCP"
        )

    def get_bound(self, bound_items, to_recordings_manager_queue):
        bound_entries = list(self._get_bound_entries(bound_items))

        def handle(msg):
            timestamp_ns = monotonic_ns()
            nested = msg.nested
            bound_entries[nested.MSG_TYPE_INT](nested)
            to_recordings_manager_queue.put(
                TimestampedLcpToCoreRecordingsManagerMsg(timestamp_ns, nested)
            )

        return handle
