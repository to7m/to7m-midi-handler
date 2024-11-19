from .logging import log_exceptions, log_exceptions_and_restart
from .tmh_msgs import try_save_unsaved_recordings
from .controllers_profiles import CONTROLLERS_PROFILE_SPECS
from .sound_modules_profiles import SOUND_MODULES_PROFILE_SPECS
from ._core import TmhCore


@log_exceptions_and_restart
def make_and_run_core():
    TmhCore(CONTROLLERS_PROFILE_SPECS, SOUND_MODULES_PROFILE_SPECS).run()


def main():
    log_exceptions(try_save_unsaved_recordings)()
    make_and_run_core()
