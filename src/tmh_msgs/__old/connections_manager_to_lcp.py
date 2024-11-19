from .bases import ConnectionsManagerToLcpMsgBase


class UnloadLcpMsg(ConnectionsManagerToLcpMsgBase):
    MSG_TYPE_INT = 0

    __slots__ = ()
