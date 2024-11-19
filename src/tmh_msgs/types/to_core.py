from .tmh import new_msg_type, ToCoreMsg


ConnectionsManagerToCoreMsg = new_msg_type(
    ToCoreMsg, 0, "ConnectionsManagerToCoreMsg",
    ["nested"]
)

LcpToCoreGlobalMsg = new_msg_type(
    ToCoreMsg, 1, "LcpToCoreGlobalMsg",
    ["nested"],
    collect_nested_reads=True
)

LcpToCorePslotMsg = new_msg_type(
    ToCoreMsg, 2, "LcpToCorePslotMsg",
    ["lcp_i", "nested"],
    collect_nested_reads=True
)

LcpToCoreRecordingsManagerMsg = new_msg_type(
    ToCoreMsg, 3, "LcpToCoreRecordingsManagerMsg",
    ["nested"],
    collect_nested_reads=True
)

RecordingsManagerToCoreMsg = new_msg_type(
    ToCoreMsg, 4, "RecordingsManagerToCoreMsg",
    ["nested"]
)
