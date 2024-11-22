from .tmh import new_msg_type, ToRecordingsManagerMsg
from .to_core import (
    LcpToCoreGlobalMsg, LcpToCorePslotMsg, LcpToCoreRecordingsManagerMsg
)


TerminateRecordingsManagerMsg = new_msg_type(
    ToRecordingsManagerMsg, 0, "TerminateRecordingsManagerMsg"
)

UpdateRecordingsMsg = new_msg_type(
    ToRecordingsManagerMsg, 1, "RecordingsUpdatedMsg"
)

GlobalStateMsg = new_msg_type(
    ToRecordingsManagerMsg, 2, "GlobalStateMsg",
    ["nesteds"]
)
GlobalStateMsg.nested_reads = LcpToCoreGlobalMsg.nested_reads

LcpStateMsg = new_msg_type(
    ToRecordingsManagerMsg, 3, "LcpStateMsg",
    ["lcp_i", "nesteds"]
)
LcpStateMsg.nested_reads = LcpToCorePslotMsg.nested_reads

# Not really to RecordingsManager, but will be serialised in the same way.
PlaybackStateMsg = new_msg_type(
    ToRecordingsManagerMsg, 4, "PlaybackStateMsg",
    ["filename_stem", "next_msg_i", ("playback_is_looped", "bool")]
)

TimestampedLcpToCoreGlobalMsg = new_msg_type(
    ToRecordingsManagerMsg, 5, "TimestampedLcpToCoreGlobalMsg",
    ["timestamp_ns", "nested"],
)
TimestampedLcpToCoreGlobalMsg.nested_reads = LcpToCoreGlobalMsg.nested_reads

TimestampedLcpToCorePslotMsg = new_msg_type(
    ToRecordingsManagerMsg, 6, "TimestampedLcpToCorePslotMsg",
    ["timestamp_ns", "lcp_i", "nested"]
)
TimestampedLcpToCorePslotMsg.nested_reads = LcpToCorePslotMsg.nested_reads

# Not really to RecordingsManager, but will be serialised in the same way.
TimestampedLcp0ToCorePslotMsg = new_msg_type(
    ToRecordingsManagerMsg, 7, "TimestampedLcp0ToCorePslotMsg",
    ["timestamp_ns", "nested"]
)
TimestampedLcp0ToCorePslotMsg.nested_reads = LcpToCorePslotMsg.nested_reads

TimestampedLcpToCoreRecordingsManagerMsg = new_msg_type(
    ToRecordingsManagerMsg, 8, "TimestampedLcpToCoreRecordingsManagerMsg",
    ["timestamp_ns", "nested"]
)
TimestampedLcpToCoreRecordingsManagerMsg.nested_reads \
    = LcpToCoreRecordingsManagerMsg.nested_reads
