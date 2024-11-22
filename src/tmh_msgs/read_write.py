from .constants import TMHM_VERSION_INT
from .types import LcpsToCoreGlobalMsg, LcpToCoreMsg


def read_and_check_version(path, file):
    tmhm_version_int = int.from_bytes(file.read(2))

    if tmhm_version_int != TMHM_VERSION_INT:
        raise Exception(
            f"path {path} uses TMHM version {tmhm_version_int}, but this"
            "instance of to7m-midi-handler only reads TMHM version "
            f"{TMHM_VERSION_INT}"
        )


def read_timestamped_msgs(file):
    try:
        while True:
            yield TimestampedMsg.read_from_file(f).nested
    except Exception as err:
        # tmp until we know what error end of file causes
        print(err)
        raise


def write_msg(file, msg):
    msg.write_to_file(file)


def write_msgs(path, msgs):
    with path('wb') as f:
        f.write(TMHM_VERSION_INT.to_bytes(8))

        for msg in msgs:
            msg.write_to_file(f)
