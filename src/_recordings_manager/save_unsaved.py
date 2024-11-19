from ..logging import log_exceptions
from .constants import RECORDINGS_DIR, UNSAVED_DIR


@log_exceptions
def try_save_unsaved_recording(
    unsaved_path, to_recordings_manager_queue=None
):
    +...
    to_recordings_manager_queue.put(RecordingsUpdatedMsg())


@log_exceptions
def try_save_unsaved_recordings(to_recordings_manager_queue=None):
    for unsaved_path in sorted(UNSAVED_DIR.iterdir()):
        try_save_unsaved_recording(unsaved_path, to_recordings_manager_queue)
