from .base import HandleSpecBase


class HandleToRecordingsManagerSpec(HandleSpecBase):
    def __init__(self):
        super().__init__(receiver_name="RecordingsManager instance")


class HandleLcpToRecordingsManagerSpec(HandleSpecBase):
    def __init__(self):
        super().__init__(
            receiver_name="RecordingsManager instance",
            from_str=" from LCP via TmhCore instance"
        )

    def get_bound(self, bound_items):
        bound_entries = list(self._get_bound_entries(bound_items))

        def handle(msg):
            nested = msg.nested
            bound_entries[nested.MSG_TYPE_INT](msg.timestamp_ns, nested)

        return handle
