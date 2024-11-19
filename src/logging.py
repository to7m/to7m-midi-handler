import sys
import traceback
import inspect
from datetime import datetime
from pathlib import Path
from threading import Thread
from queue import Queue

import __main__


ALLOW_RESTART = True
_LOG_PATH = Path(__main__.__file__).parent / "log.txt"


class BreakWithoutLogging(Exception):
    pass


_queue = Queue()


def _get_msg_start():
    return f"<{str(datetime.now())[:-3]}>  "


def _get_err_start(*, additional_frames=0):
    frame = inspect.stack()[additional_frames + 1]

    end_of_start = f"ERROR ({frame.filename} line {frame.lineno}): "
    return _get_msg_start() + end_of_start


def _get_traceback_str(exc, indent="    "):
    entries = traceback.format_exception(exc, value=exc, tb=exc.__traceback__)
    unindented = ''.join(entries)[:-1]
    return indent + unindented.replace('\n', f"\n{indent}")


def _get_logger_thread_type_err_str(item):
    body = f"logged item {item} is of type {type(item)} instead of str"
    return f"{_get_err_start()}{body}\n"


def _get_logger_thread_unanticipated_exc_str(exc):
    body = "unanticipated logging exception:\n" + _get_traceback_str(exc)
    return f"{_get_err_start()}{body}\n"


def _logger():
    with _LOG_PATH.open('a') as f:
        try:
            while True:
                s = _queue.get()

                if s is None:
                    break
                elif type(s) is not str:
                    s = _get_logger_thread_type_err_str(s)

                f.write(s)
                f.flush()
                print(s, end='', flush=True)
        except BaseException as exc:
            s = _get_logger_thread_unanticipated_exc_str(exc)

            f.write(s)
            f.flush()
            print(s, end='', flush=True)


def _format_print_style_args(xargs, sep=' ', end='\n'):
    return sep.join(str(xarg) for xarg in xargs) + end


def start_logging_thread():
    Thread(target=_logger).start()


def stop_logging_thread():
    _queue.put(None)


def log_str(s):
    _queue.put(s)


def log_msg(*xargs):
    log_str(_get_msg_start() + _format_print_style_args(xargs))


def log_err(*xargs, additional_frames=0):
    start = _get_err_start(additional_frames=additional_frames + 1)
    content = _format_print_style_args(xargs)
    log_str(start + content)


def log_traceback(exc):
    err_msg = "EXCEPTION RAISED:\n" + _get_traceback_str(exc)
    log_msg(err_msg)


def log_exceptions(callable_):
    def wrapped(*xargs, **kwargs):
        try:
            return callable_(*xargs, **kwargs)
        except BreakWithoutLogging:
            return
        except BaseException as exc:
            exc.__traceback__ = exc.__traceback__.tb_next
            log_traceback(exc)

    return wrapped


def log_exceptions_and_restart(callable_):
    def wrapped(*xargs, **kwargs):
        while True:
            try:
                return callable_(*xargs, **kwargs)
            except BreakWithoutLogging:
                return
            except BaseException as exc:
                exc.__traceback__ = exc.__traceback__.tb_next
                log_traceback(exc)

                if ALLOW_RESTART:
                    log_msg("attempting restart of callable")
                else:
                    log_msg("not attempting restart of callable")
                    break

    return wrapped
