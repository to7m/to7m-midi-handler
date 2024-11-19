from subprocess import check_output


class To7mAconnectError(Exception):
    pass


class ParseError(To7mAconnectError):
    pass


class _Connection:
    def __init__(self, client_num, port_num):
        self.client_num = client_num
        self.port_num = port_num

    @classmethod
    def from_nums_str(cls, nums_str):
        client_num_str, port_num_str = nums_str.split(':')
        client_num, port_num = int(client_num_str), int(port_num_str)
        return cls(client_num, port_num)


class _Port:
    def __init__(self, name, num, froms, tos):
        self.name = name
        self.num = num
        self.froms = froms
        self.tos = tos

    @staticmethod
    def _make_connections(connections_lines, direction):
        for line in connections_lines:
            if direction in line:
                break
        else:  # if no break
            return

        for nums_str in line.split(": ")[1].split(", "):
            yield _Connection.from_nums_str(nums_str)

    @classmethod
    def from_lines(cls, lines):
        header_line, *connections_lines = lines

        num_segment, name, _ = header_line.split("'")
        num = int(num_segment)

        froms = list(cls._make_connections(connections_lines, "From"))
        tos = list(cls._make_connections(connections_lines, "To"))

        return cls(name, num, froms, tos)


class _Client:
    def __init__(self, name, num, ports):
        self.name = name
        self.num = num
        self.ports = ports

    @staticmethod
    def _make_ports(lines):
        start_line_nums = [
            i for i, line in enumerate(lines)
            if not line.startswith('\t')
        ]
        stop_line_nums = [*start_line_nums[1:], len(lines)]

        for start, stop in zip(start_line_nums, stop_line_nums):
            yield _Port.from_lines(lines[start:stop])

    @classmethod
    def from_lines(cls, lines):
        header_line, *ports_lines = lines

        num_segment, name, _ = header_line.split("'")
        num = int(num_segment[7:-2])

        ports = list(cls._make_ports(ports_lines))

        return cls(name, num, ports)


class Aconnect:
    def __init__(self, clients=None):
        if clients is None:
            raw_output = self.make_raw_output()
            clients = self._clients_from_raw_output(raw_output)

        self.clients = clients

    @staticmethod
    def _make_clients(lines):
        start_line_nums = [
            i for i, line in enumerate(lines)
            if line.startswith("client")
        ]
        stop_line_nums = [*start_line_nums[1:], len(lines)]

        for start, stop in zip(start_line_nums, stop_line_nums):
            yield _Client.from_lines(lines[start:stop])

    @classmethod
    def _clients_from_raw_output(cls, raw_output):
        lines = raw_output.decode().split('\n')[:-1]
        return list(cls._make_clients(lines))

    @staticmethod
    def make_raw_output():
        return check_output(["aconnect", '-l'])

    @classmethod
    def from_raw_output(cls, raw_output):
        clients = cls._clients_from_raw_output(raw_output)
        return cls(clients)

    def get_device_counts(self):
        device_counts = {}

        for client in self.clients:
            if client.name not in device_counts:
                device_counts[client.name] = 0

            device_counts[client.name] += 1

        return device_counts


aconnect = Aconnect()
