class TmpExampleControllersProfile:
    def __init__(self, send_lcp_to_core_msg):
        super.__init__(send_lcp_to_core_msg)

        self._vel_curve

        self._active_nrc_indices = ()
        self._dormant_nrc_indices = [set(), set(), set(), ...]
        self._notes_for_nrcs = []

    @MidiMsgCallbackMethodFactory(port_i=0, msg_start=[144])
    def handle_raw_note_on(self, msg):
        if velocity == 0:
            self._to_tmh_core(NoteOffMsg(0, midi_note))
        else:
            self._to_tmh_core(LazyNoteOnWithVelMsg(0, midi_note, velocity, self._vel_curve))

    ignore = IgnoreMidiMsgsMethod(port_i=0, msg_starts=[[144, 60], [144, 61]])



from ...to7m_exec import func_from_str


def vel_curve_calculator_to_lut(
    calculator, lowest_midi_note, highest_midi_note
):
    lut = np.empty((128, 128), -2, dtype=np.float32)
    for midi_note in range(lowest_midi_note, highest_midi_note + 1):
        for velocity in range(1, 128):
            lut[midi_note, velocity] = calculator(midi_note, velocity)

    return lut.__getitem__


def make_handle_raw_note_on(
    hnrc_i, hnrc_vel_curve, snrc_ranges_and_transpositions_for_pnrc_indices,
    dst_callable,
    lowest_midi_note=None, highest_midi_note=None, verify_in_range=True,
    zero_vel_action="raise",
    send_lazy=False
):
    globals_ = {"hnrc_i": hnrc_i, "hnrc_vel_curve": hnrc_vel_curve}

    if send_lazy:
        fn_str_lines = [
            "dst_callable(",
            "    LazyNoteOnWithVelMsg(",
            "        hnrc_i, midi_note, velocity,",
            "        hnrc_vel_curve",
            "    )",
            ")"
        ]
    else:
        fn_str_lines = [
            "for nonlazy_msg in LazyNoteOnWithVelMsg(",
            "    hnrc_i, midi_note, velocity,",
            "    hnrc_vel_curve",
            "):",
            "    dst_callable(nonlazy_msg)"
        ]

    if zero_vel_action == "raise":
        globals_["zero_vel_err"] = ControllersProfileError(
            "zero velocity received, but handle_raw_note_on was generated "
            'with zero_vel_action="raise"'
        )
        fn_str_lines = [
            "if velocity:",
            *(f"    {line}" for line in fn_str_lines),
            "else:",
            "    raise zero_vel_err"
        ]
    elif zero_vel_action == "send_note_off":
        fn_str_lines = [
            "if velocity:",
            *(f"    {line}" for line in fn_str_lines),
            "else:",
            "    dst_callable(",
            "        NoteOffMsg(",
            "            hnrc_i, midi_note",
            "        )",
            "    )"
        ]
    elif zero_vel_action != "no_check":
        raise ValueError(
            'zero_vel_action should be either "raise", "send_note_off", or '
            '"no_check"'
        )

    if verify_in_range:
        if None in (lowest_midi_note, highest_midi_note):
            raise TypeError(
                "unless verify_in_range=False, lowest_midi_note and "
                "highest_midi_note should be provided"
            )

        globals_["lowest_midi_note"] = lowest_midi_note
        globals_["highest_midi_note"] = highest_midi_note
        globals_["out_of_range_err"] = ControllersProfileError(
            f"midi_note out of range {lowest_midi_note} <= x <= "
            f"{highest_midi_note} received"
        )

        fn_str_lines = [
            "if lowest_midi_note <= midi_note <= highest_midi_note:",
            *(f"    {line}" for line in fn_str_lines),
            "else:",
            "    raise out_of_range_err"
        ]

    fn_str_lines = [
        "def handle_raw_note_on(midi_note, velocity):",
        *(f"    {line}" for line in fn_str_lines)
    ]

    fn_str = '\n'.join(fn_str_lines)

    handle_raw_note_on = func_from_str(
        fn_str, globals_
    )

    return handle_raw_note_on
