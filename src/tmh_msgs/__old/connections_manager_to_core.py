from .bases import ConnectionsManagerToCoreMsgBase


class ConnectLcpMsg(ConnectionsManagerToCoreMsgBase):
    MSG_TYPE_INT = 0

    __slots__ = "lcp_i",

    def __init__(self, lcp_i):
        self.lcp_i = lcp_i
