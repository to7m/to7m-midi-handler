from .to_core import new_msg_type, LcpToCorePslotMsg


RegisterPslotMsg = new_msg_type(
    LcpToCorePslotMsg, 0, "RegisterPslotMsg",
    ["pslot_i"]
)

DeregisterPslotMsg = new_msg_type(
    LcpToCorePslotMsg, 1, "DeregisterPslotMsg",
    ["pslot_i"]
)

ResetPslotStateMsg = new_msg_type(
    LcpToCorePslotMsg, 2, "ResetPslotStateMsg",
    ["pslot_i"]
)
