# !non-urgent: add metaclass stuff to check methods are there (basically do explicit_inheritance module)
# !non-urgent: add serialisation and deserialisation


from ._errors import TmhMsgsError


class TmhMsgsInvalidNewClassError(TmhMsgsError):
    pass


class _MsgTypeIntCount:
    def __init__(self):
        self._count = 0

    def check_and_increment_from(self, msg_type_int):
        if msg_type_int == self._count:
            self._count += 1
        else:
            raise TmhMsgsInvalidNewClassError(
                f"expected MSG_TYPE_INT {self._count}, but received "
                f"{msg_type_int}"
            )


class _TmhMsgMeta(type):
    def __new__(cls, name, bases, namespace, is_base=False):
        ending = "MsgBase" if is_base else "Msg"
        if not name.endswith(ending):
            raise TmhMsgsInvalidNewClassError(
                f"class name should end with {ending!r}"
            )

        inst = super().__new__(cls, name, bases, namespace)

        if not is_base:
            inst._check_and_increment_msg_type_int_count()

        return inst

    def _check_and_increment_msg_type_int_count(self):
        for attr in "MSG_TYPE_INT_COUNT", "MSG_TYPE_INT":
            if not hasattr(self, attr):
                raise TmhMsgsInvalidNewClassError(
                    "non-base _TmhMsgMeta instances should inherit a "
                    "MSG_TYPE_INT_COUNT attribute and specify a MSG_TYPE_INT "
                    "attribute"
                )

        self.MSG_TYPE_INT_COUNT.check_and_increment_from(self.MSG_TYPE_INT)


class _TmhMsgBase(metaclass=_TmhMsgMeta, is_base=True):
    pass


class ConnectionsManagerToCoreMsgBase(_TmhMsgBase, is_base=True):
    MSG_TYPE_INT_COUNT = _MsgTypeIntCount()


class _InternalToLcpMsgBase(_TmhMsgBase, is_base=True):
    MSG_TYPE_INT_COUNT = _MsgTypeIntCount()


class ConnectionsManagerToLcpMsgBase(_InternalToLcpMsgBase, is_base=True):
    pass


class CoreToLcpMsgBase(_InternalToLcpMsgBase, is_base=True):
    pass


class _LcpToCoreMsgBase(_TmhMsgBase, is_base=True):
    MSG_TYPE_INT_COUNT = _MsgTypeIntCount()


class LcpToCoreSerialisableMsgBase(_LcpToCoreMsgBase, is_base=True):
    pass


class LcpToCoreUnserialisableMsgBase(_LcpToCoreMsgBase, is_base=True):
    pass
