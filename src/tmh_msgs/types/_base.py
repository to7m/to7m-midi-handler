from ...logging import log_err
from ...to7m_exec import Container
from ._params import Params, sanitise_params


class TmhMsgMeta(type):
    def __new__(
        cls, name, bases, namespace, collect_nested_reads=False
    ):
        inst = super().__new__(name, bases, namespace)

        if collect_nested_reads:
            inst.nested_reads = []
        else:
            inst_nested_reads = None

        cls._try_add_to_base_nested_reads(bases, inst)

        return inst

    @staticmethod
    def _try_add_to_base_nested_reads(bases, inst):
        if len(bases) == 0:
            pass
        elif len(bases) == 1:
            nested_reads = bases[0].nested_reads

            if nested_reads is None:
                return

            if len(nested_reads) == 256:
                raise Exception("limit of 256 subclasses reached")

            if inst.MSG_TYPE_INT != len(nested_reads):
                raise Exception(
                    f"expected MSG_TYPE_INT {len(nested_reads)}, but "
                    f"received {inst.MSG_TYPE_INT}"
                )

            nested_reads.append(inst.read_from_file)
        else:
            raise Exception(
                "only 1 base should be used for a TmhMsgMeta instance"
            )

    @staticmethod
    def _indented(lines):
        for line in lines:
            if line:
                yield f"    {line}"
            else:
                yield ''

    @classmethod
    def _make_init_lines(cls, params, param_names):
        yield f'def __init__({", ".join(["self", *param_names])}):'

        if not params:
            yield "    pass"
            return

        for param in params[:-1]:
            yield from cls._indented(param.init_lines)

        yield from cls._indented(params[-1].init_lines)

    @classmethod
    def _make_read_from_file_lines(cls, param_names):
        yield "@classmethod"
        yield "def read_from_file(cls, file):"

        for param in params:
            yield from cls._indented(param.read_lines)
            yield ''

        yield f'return cls({", ".join(param_names)})'

    @classmethod
    def _make_write_to_file_lines(cls, msg_type_int, params):
        yield "def write_to_file(self, file):"
        yield f'    file.write({msg_type_int.to_bytes(1)!r}")'

        for param in params:
            yield ''
            yield from cls._indented(param.write_lines)

    @classmethod
    def _make_methods(cls, msg_type_int, params):
        param_names = [param.name for param in params]

        str_ = '\n'.join([
            *cls._make_init_lines(params, param_names), '', '',
            *cls._make_read_from_file_lines(), '', '',
            *cls._make_write_to_file_lines(msg_type_int), ''
        ])

        return Container(str_).exec_()

    @classmethod
    def from_args(
        cls, base, msg_type_int, msg_type_name, params=None, *, is_base=False
    ):
        params = sanitise_params(params)
        compiled_from_str = cls._make_methods(msg_type_int, params)

        namespace = {
            "MSG_TYPE_INT": msg_type_int,
            "__slots__": [param.name for param in params],
            "__init__": compiled_from_str["__init__"],
            "read_from_file": compiled_from_str["read_from_file"],
            "write_to_file": compiled_from_str["write_to_file"]
        }

        return _TmhMsgMeta(msg_type_name, (base,), namespace, is_base=is_base)


new_msg_type = TmhMsgMeta.from_args


class TmhMsg(metaclass=_TmhMsgMeta, collect_nested_reads=True):
    @classmethod
    def _log_err(cls, err_str):
        log_err(f"{cls.__name__}:", err_str)
