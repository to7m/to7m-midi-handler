from ._base import new_msg_type, TmhMsg


ToCoreMsg = new_msg_type(
    TmhMsg, 0, "ToCoreMsg",
    collect_nested_reads=True
)

ToRecordingsManagerMsg = new_msg_type(
    TmhMsg, 1, "ToRecordingsManagerMsg",
    collect_nested_reads=True
)
