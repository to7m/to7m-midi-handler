from ..logging import log_exceptions
from .constants import UNSAVED_DIR, SAVED_DIR
from .types import (
    UpdateRecordingsMsg
)
from ._read_write import (
    read_and_check_version, read_state_msgs, read_timestamped_msgs
)


@log_exceptions
def try_save_unsaved_recording(
    unsaved_path, to_recordings_manager_queue=None
):
    with unsaved_path.open('rb') as f:
        read_and_check_version(f)
        state_msgs = list(read_state_msgs(f))
        timestamped_msgs = list(read_timestamped_msgs(f))

    +...
    segments = _split_by_playback_msgs(raw_msgs)


    ... assume playback_segments

    _check_no_lcp_0

    last_timestamps_ns = raw_msgs[-1][1].timestamp_ns

    global_msgs, lcp_msgs = _categorise_raw_msgs(raw_msgs)
    playback_infos = list(_get_playback_infos(global_msgs, len(raw_msgs)))
    lcp_msgs = list(_address_hanging_playbacks(lcp_msgs, playback_infos))
    lcp_msgs = list(_fix_pslot_indices(lcp_msgs, last_timestamp_ns))

    return +bool


def try_save_unsaved_recordings(to_recordings_manager_queue=None):
    if UNSAVED_DIR.exists():
        new_saved_recordings = False

        for path in sorted(unsaved_dir.iterdir()):
            new_saved_recordings |= try_save_unsaved_recording(path)

        if new_saved_recordings and to_recordings_manager_queue:
            to_recordings_manager_queue.put(UpdateRecordingsMsg())














+...
def _get_new_playback_info(nested, old_playback_info):
    if type(nested) is StartPlaybackMsg:
        path = RECORDINGS_DIR / f"{msg.nested.filename_stem}.tmhm"
        start_i = msg.nested_filename_stem
    elif type(msg.nested) is StopPlaybackMsg:
        if old_path is None:
            raise Exception(
                "StopPlaybackMsg tried to stop inexistent playback"
            )

            return None


def _split_by_playback_msgs(msgs):
    playback_info = None
    segment_msgs = []

    for msg in msgs:
        if type(msg.nested) in (StartPlaybackMsg, StopPlaybackMsg):
            if segment_msgs:
                yield playback_info, segment_msgs

            segment_path = _get_new_pl(msg.nested, segment_path)
            segment_msgs = []

    if segment_msgs:
        yield segment_path, segment_msgs


def _categorise_raw_msgs(all_raw_msgs):
    global_msgs, lcp_msgs = [], []
    for i, msg in raw_msgs:
        if type(msg) is TimestampedLcpsToCoreGlobalMsg:
            global_msgs.append((i, msg))
        elif type(msg) is TimestampedLcpToCoreMsg:
            lcp_msgs.append((i, msg))

    return global_msgs, lcp_msgs


def _get_playback_infos(global_msgs, last_i):
    path = None
    start_i = None

    for i, msg in global_msgs:
        if type(msg.nested) is StartPlaybackMsg:
            if path is None:
                path = RECORDINGS_DIR / f"{msg.nested.filename_stem}.tmhm"
                start_i = i
            else:
                raise Exception(
                    "StartPlaybackMsg tried to play over current playback"
                )
        elif type(msg.nested) is StopPlaybackMsg:
            stop_i = i
            yield path, start_i, stop_i

            path = None
            start_i = None

    if path is not None:
        log_err("playback left on in unsaved recording")

        yield path, start_i, last_i + 1

def _get_first_false_entry_i(list_):
    for i, val in list_:
        if not val:
            return i

    list_.append(False)
    return len(list_) - 1


def _address_hanging_playbacks(lcp_msgs, playback_infos):
    playback_infos_iter = iter(playback_infos_iter)
    path, start_i, stop_i = next(playback_infos_iter)

    lcp0_pslot_indices = set()

    for i, msg in lcp_msgs:
        if msg.lcp_i != 0:
            continue

        if i < start_i:
            raise Exception("lcp_i=0 when despite no recording playing")
        elif start_i < i < stop_i:
            continue
        elif i > stop_i:
            path, start_i, stop_i = next(playback_infos_iter)


def _fix_pslot_indices(lcp_msgs, last_timestamp_ns):
    """Change all "pslot_i" attributes to fit into the same LCP."""

    new_pslots_for_old = {}
    new_pslots_are_active = []

    for msg in lcp_msgs:
        old_key = msg.lcp_i, msg.nested.pslot_i

        if type(msg.nested) is RegisterPslotMsg:
            if old_key in new_pslots_for_old:
                raise Exception(
                    "RegisterPslotMsg tried to register existing PSLOT"
                )

            new_pslot_i = _get_first_false_entry_i(new_pslots_are_active)
            new_pslots_for_old[old_key] = new_pslot_i
            new_pslots_are_active[new_pslot_i] = True
        elif type(msg.nested) is DeregisterPslotMsg:
            if old_key not in new_pslots_for_old:
                raise Exception(
                    "DeregisterPslotMsg tried to deregister inexistent PSLOT"
                )

            new_pslot_i = new_pslots_for_old.pop(old_key)
            new_pslots_are_active[new_pslot_i] = False

        msg.nested.pslot_i = new_pslot_i
        yield msg

    if new_pslots_for_old:
        log_err(
            "some PSLOTS left registered in unsaved recording; adding "
            "DeregisterPslotMsg(s)"
        )

        for (lcp_i, _), new_pslot_i in new_pslots_for_old.items():
            yield TimestampedLcpToCoreMsg(
                timestamp_ns=last_timestamp_ns,
                lcp_i=lcp_i
                nested=DeregisterPslotMsg(new_pslot_i)
            )

