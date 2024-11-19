from .to_core import new_msg_type, LcpToCoreGlobal


ResetGlobalStateMsg = new_msg_type(
    LcpToCoreGlobal, 0, "ResetGlobalStateMsg"
)
