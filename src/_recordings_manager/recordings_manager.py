from threading import Thread
from queue import Queue

from .constants import RECORDINGS_DIR, UNSAVED_DIR
from .save_unsaved import try_save_unsaved_recordings


class RecordingsManager:
    HANDLE_SPEC = HandleToRecordingsManagerSpec()

    HANDLE_LCP_TO_RECORDINGS_MANAGER_SPEC = HandleLcpToRecordingsManagerSpec()
    HANDLE_SPEC.register_callback(
        HANDLE_LCP_TO_RECORDINGS_MANAGER_SPEC,
        TimestampedLcpToCoreRecordingsManagerMsg.MSG_TYPE_INT,
        binding_needed=True
    )

    def __init__(self, to_core_queue):
        self.queue = Queue()
        self.to_core_queue = to_core_queue

        self._handle = self._bind(self.HANDLE_SPEC)

        self._state_msgs = []
        self._tmp_file = None

        self._recordings_player = RecordingsPlayer(to_core_queue)

    def _bind(self, bindable):
        if isinstance(bindable, RecursivelyBindableBase):
            bound_items = [
                self._bind(unbound_item)
                for unbound_item in bindable.get_unbound_items()
            ]
            return bindable.get_bound(bound_items)
        else:
            return bindable.__get__(self, type(self))

    def _get_unsorted_filename_stems(self):
        for path in RECORDINGS_DIR.iterdir():
            if path.suffix == ".tmhm":
                yield path

    def _write_tmp_header(self, timestamp_ns):
        write_tmhm_version_int(self._tmp_file)

        self._state_msgs.append(
            PlaybackStateMsg(+...)
        )

        for msg in self._state_msgs:
            msg.write_to_file(self._tmp_file)

        self._state_msgs = None

        TimestampedLcpToCoreRecordingsManagerMsg(
            timestamp_ns, StartRecordingMsg()
        ).write_to_file(self._tmp_file)

    def _try_stop_playback(self):
        +...

    def _try_write_msg_to_file(self, msg):
        if self._tmp_file:
            msg.write_to_file(self._tmp_file)

    def _run(self):
        get = self.queue.get
        handle = self._handle

        while True:
            try:
                while True:
                    handle(get())
            except StopIteration:
                break

    @HANDLE_SPEC.callback_method_registrar_for(
        TerminateRecordingsManagerMsg.MSG_TYPE_INT
    )
    def terminate_recordings_manager(self, _):
        raise StopIteration

    @HANDLE_SPEC.callback_method_registrar_for(
        GlobalStateMsg.MSG_TYPE_INT
    )
    def handle_global_state(self, msg):
        self._state_msgs = [msg]

    @HANDLE_SPEC.callback_method_registrar_for(
        LcpStateMsg.MSG_TYPE_INT
    )
    def handle_lcp_state(self, msg):
        self._state_msgs.append(msg)

    @HANDLE_SPEC.callback_method_registrar_for(
        TimestampedLcpToCoreGlobalMsg.MSG_TYPE_INT,
        TimestampedLcpToCorePslotMsg.MSG_TYPE_INT
    )
    def handle_lcp_to_core_global_and_pslot(self, msg):
        if self._tmp_file:
            msg.write_to_file(self._tmp_file)

    @HANDLE_LCP_TO_RECORDINGS_MANAGER_SPEC.callback_method_registrar_for(
        StartRecordingMsg.MSG_TYPE_INT
    )
    def handle_start_recording(self, timestamp_ns, msg):
        if self._tmp_path:
            log_err(
                "recording already in progress; stopping current recording"
            )

            self.handle_stop_recording(timestamp_ns, StopRecordingMsg())

        tmp_path = UNSAVED_DIR / f"{msg.filename_stem}.tmhm_unsaved"
        self._tmp_file = tmp_path.open('wb')
        self._write_tmp_header(timestamp_ns)

    @HANDLE_LCP_TO_RECORDINGS_MANAGER_SPEC.callback_method_registrar_for(
        StopRecordingMsg.MSG_TYPE_INT
    )
    def handle_stop_recording(self, timestamp_ns, msg):
        if not self._tmp_file:
            log_err("can't stop recording that isn't happening")
            return

        msg = TimestampedLcpToCoreRecordingsManagerMsg(timestamp_ns, msg)
        msg.write_to_file(self._tmp_file)

        self._tmp_file.close()
        self._tmp_file = None

        try_save_unsaved_recordings(to_recordings_manager_queue=self.queue)

    @HANDLE_LCP_TO_RECORDINGS_MANAGER_SPEC.callback_method_registrar_for(
        StartPlaybackMsg.MSG_TYPE_INT
    )
    def handle_start_playback(self, timestamp_ns, msg):
        self._try_stop_playback()

        # load and buffer playback file
        +...

        msg = TimestampedLcpToCoreRecordingsManagerMsg(timestamp_ns, msg)
        self._try_write_msg_to_file(msg)

    @HANDLE_LCP_TO_RECORDINGS_MANAGER_SPEC.callback_method_registrar_for(
        StopPlaybackMsg.MSG_TYPE_INT
    )
    def handle_stop_playback(self, timestamp_ns, msg):
        self._try_stop_playback()

        msg = TimestampedLcpToCoreRecordingsManagerMsg(timestamp_ns, msg)
        self._try_write_msg_to_file(msg)


    @HANDLE_SPEC.callback_method_registrar_for(
        UpdateRecordingsMsg.MSG_TYPE_INT
    )
    def handle_update_recordings(self, msg):
        filename_stems = sorted(self._get_unsorted_filename_stems())
        self.to_core_queue.put(FilenameStemsMsg(filename_stems))

    def start(self):
        Thread(target=self._run).start()

    def stop(self):
        self._to_recordings_manager_queue.put(TerminateRecordingsManagerMsg())

