from .to_core import new_msg_type, LcpToCoreRecordingsManager


StartRecordingMsg = new_msg_type(
    LcpToCoreRecordingsManager, 0, "StartRecordingMsg",
    ["filename_stem", ("include_globals", "bool")]
)

StopRecordingMsg = new_msg_type(
    LcpToCoreRecordingsManager, 1, "StopRecordingMsg"
)

StartPlaybackMsg = new_msg_type(
    LcpToCoreRecordingsManager, 2, "StartPlaybackMsg",
    ["filename_stem", ("playback_globals", "bool"), ("loop", "bool")]
)

StopPlaybackMsg = new_msg_type(
    LcpToCoreRecordingsManager, 3, "StopPlaybackMsg"
)

GetFilenameStemsMsg = new_msg_type(
    LcpToCoreRecordingsManager, 4, "GetFilenameStemsMsg"
)

RenameRecordingMsg = new_msg_type(
    LcpToCoreRecordingsManager, 5, "RenameRecordingMsg",
    {
        "old_filename_stem": "filename_stem",
        "new_filename_stem": "filename_stem"
    }
)

DeleteRecordingMsg = new_msg_type(
    LcpToCoreRecordingsManager, 6, "DeleteRecordingMsg",
    ["filename_stem"]
)
