from ....logging import log_err


class HandleSpecBase:
    def __init__(self, controllers_profile_name, *, port_i):
        self.controllers_profile_name = controllers_profile_name
        self.port_i = port_i

        self.report_msg = self._make_report_msg()
        self.ignore_msg = lambda msg: None

    def _make_report_msg(self):
        err_str = (
            f"{self.controllers_profile_name} instance received invalid "
            f"message from port {self.port_i}:"
        )

        def report_msg(msg):
            log_err(err_str, msg)

        return report_msg
