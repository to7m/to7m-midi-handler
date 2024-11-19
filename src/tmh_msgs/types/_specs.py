SPECS_FOR_SPEC_NAMES = {}


class Spec(type):
    def __new__(cls, name, bases, namespace):
        bases = SpecBase,

        for method_type in "init", "write", "read":
            method_name = f"get_{method_type}_lines"
            if method_name in namespace:
                namespace[method_name] = staticmethod(namespace[method_name])

        inst = super().__new__(cls, name, bases, namespace)

        SPECS_FOR_SPEC_NAMES[name[:-5]] = inst
        return inst


class SpecBase(metaclass=Spec):
    def __new__(*xargs, **kwargs):
        raise Exception(
            "Spec instances (usually SpecBase subclasses) should not be "
            "instantiated"
        )


class nested_spec(SpecBase):
    def get_init_lines(name):
        yield f"self.{name} = {name}"

    def get_read_lines(name):
        yield "_msg_type_int = int.from_bytes(file.read(1))"
        yield f"_nested_read = self.nested_reads[_msg_type_int]"
        yield f"{name} = _nested_read(file)"

    def get_write_lines(name):
        yield f"self.{name}.write_to_file(file)"


class nesteds_spec(SpecBase):
    def get_init_lines(name):
        yield f"if type({name}) is list:"
        yield f"    self.{name} = {name}"
        yield 'else:'
        yield f'    self._log_err(f"name should be a list of msgs")'

    def get_read_lines(name):
        yield "_len = int.from_bytes(file.read(2))"
        yield f"{name} = []"
        yield "for _ in range(_len):"
        yield "    _msg_type_int = int.from_bytes(file.read(1))"
        yield f"    _nested_read = self.nested_reads[_msg_type_int]"
        yield f"    {name}.append(_nested_read(file))"

    def get_write_lines(name):
        yield f"_len = len(self.{name})"
        yield f"file.write(_len.to_bytes(2))"
        yield f"for msg in self.{name}:"
        yield "    msg.write_to_file(file)"


class bool_spec(SpecBase):
    def get_init_lines(name):
        yield f"if type({name}) is bool:"
        yield f"    self.{name} = {name}"
        yield "else:"
        yield f'    self._log_err("{name} should be a bool")'

    def get_read_lines(name):
        yield f"{name} = bool(int.from_bytes(file.read(0)))"

    def get_write_lines(name):
        yield f'file.write(b"\xff" if self.{name} else b"\x00")'


def make_int_spec(*, byte_len, signed):
    bit_len = byte_len * 8
    start = -(1 << (bit_len - 1)) if signed else 0
    stop = 1 << (bit_len - (1 if signed else 0))

    def get_init_lines(name):
        yield f"if type({name}) is int and {start} <= {name} < {stop}:"
        yield f"    self.{name} = {name}"
        yield "else:"
        yield (
            f'    self._log_err("{name} should be an int in range '
            f'{start} <= x < {stop}")'
        )

    def get_read_lines(name):
        yield f"{name} = int.from_bytes(file.read({byte_len}))"

    def get_write_lines(name):
        yield f"file.write(self.{name}.to_bytes({byte_len}))"

    name = f"int{bit_len}_spec" if signed else f"uint{bit_len}_spec"
    namespace = {
        "get_init_lines": get_init_lines,
        "get_read_lines": get_read_lines,
        "get_write_lines": get_write_lines
    }
    return Spec(name, (), namespace)


uint8_spec = make_uint_spec(byte_len=1, signed=False)
int16_spec = make_uint_spec(byte_len=2, signed=True)
uint64_spec = make_uint_spec(byte_len=8, signed=False)


class filename_stem_spec(SpecBase):
    def get_init_lines(name):
        yield f"if type({name}) is str:"
        yield f"    if len({name}) >= 256:"
        yield (
            f'        self._log_err("{name} should be fewer than 256 '
            f'characters long")'
        )
        yield ''
        yield f"    for char in {name}:"
        yield "        if not char.isalnum() and char not in '-_ ':"
        yield (
            f'            self._log_err("{name} should consist only of '
            "characters 0-9, a-z, A-Z, '-', '_', and ' '\")"
        )
        yield ''
        yield f"    self.{name} = {name}"
        yield 'else:'
        yield f'    self._log_err("{name} should be a str")'

    def get_read_lines(name):
        yield "_len = int.from_bytes(file.read(1))"
        yield f"{name} = file.read(_len).decode()"

    def get_write_lines(name):
        yield f"_len = len(self.{name})"
        yield "file.write(_len.to_bytes(1))"
        yield f"file.write(self._{name}.encode())"


class true_vel_spec(SpecBase):
    def get_init_lines(name):
        yield f"if type({name}) is float:"
        yield f"    if {name} == 0.0 or 1.0 <= {name} <= 10.0:"
        yield f"        self.{name} = {name}"
        yield "    else:"
        yield (
            f'        self._log_err("{name} should be either 0.0, or in the '
            'range 1.0 <= x <= 10.0")'
        )
        yield "else:"
        yield f'    self._log_err("{name} should be a float")'

    +...
