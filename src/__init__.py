# submodule import order:
#   logging
#   to7m_exec
#   to7m_aconnect
#   recursively_bindable
#   tmh_msgs
#   curves
#   connections_profiles_shared
#   _connections
#   _core
#   controllers_profiles
#   sound_modules_profiles
#   _main


from pathlib import Path

import __main__
from .logging import (
    start_logging_thread, stop_logging_thread,
    log_str, log_msg, log_traceback
)


executable_path = Path(__main__.__file__)


def run_tmh():
    start_logging_thread()

    try:
        log_msg(f"starting {executable_path.name} ({executable_path})")

        from ._main import main

        main()
    except BaseException as exc:
        log_traceback(exc)
        log_msg("FATAL ERROR")
    else:
        log_msg(f"exiting {executable_path.name}")
    finally:
        log_str('\n' + '#' * 79 + '\n\n')
        stop_logging_thread()
