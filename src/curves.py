import numpy as np

from .error import To7mMidiHandlerError


class CurvesError(Exception):
    pass


class MidiToTrueVelCurve(np.ndarray):
    def __call__(self, midi_note, midi_vel):
        return self[midi_note, midi_vel]

    @classmethod
    def empty(cls):
        inst = cls((128, 128), dtype=np.float32)
        inst[:, 0] = 0.0
        return inst

    def set_note_from_pairs(self, midi_note, midi_true_pairs):
        for (start_midi, start_true), (stop_midi, stop_true) in zip(
            midi_true_pairs[:-1], midi_true_pairs[1:]
        ):
            for midi in range(start_midi, stop_midi):
                progress = (midi - start_midi) / (stop_midi - start_midi)
                true = start_true + (stop_true - start_true) * progress
                self[midi_note, midi] = true

        midi, true = midi_true_pairs[-1]
        self[midi_note, midi] = true


class TrueToMidiVelCurve:
    __slots__ = [
        "_comparisons", "_pairs_len", "_start_i", "_offsets",
        "_true_vels", "_gradients_and_intercepts",
        "_call"
    ]

    def __init__(self, *, comparisons):
        self._comparisons = comparisons
        self._pairs_len = 2 ** comparisons + 1
        self._start_i = 2 ** comparisons - 1
        self._offsets = [2 ** x for x in range(comparisons - 1, -1, -1)]

        self._true_vels, self._gradients_and_intercepts = self._make_arrs()

        self._call = self._make_call()

    def __call__(self, midi_note, true_vel):
        return self._call(midi_note, true_vel)

    def _make_arrs(self):
        true_vels = np.zeros(
            (128, 2 * 2 ** self._comparisons - 2),
            dtype=np.float32
        )
        gradients_and_intercepts = np.full(
            (128, 2 * 2 ** self._comparisons - 1, 2),
            (0.0, 64.0),
            dtype=np.float32
        )

        return true_vels, gradients_and_intercepts

    def _make_call(self):
        start_i = self._start_i
        offsets = self._offsets
        true_vels = self._true_vels
        gradients_and_intercepts = self._gradients_and_intercepts

        def call(midi_note, true_vel):
            i = start_i

            true_vels_for_note = true_vels[midi_note]
            for offset in offsets:
                i += offset if true_vel >= true_vels_for_note[i] else -offset

            a, b = gradients_and_intercepts[midi_note, i]

            return round(a * true_vel + b)

        return call

    def _padded_pairs(self, true_midi_pairs):
        additional_pairs_needed = self._pairs_len - len(true_midi_pairs)

        if additional_pairs_needed < 0:
            raise CurvesError("true_midi_pairs is too long")
        elif additional_pairs_needed == 0:
            yield from true_midi_pairs
        else:
            start_true, start_midi = true_midi_pairs[0]
            stop_true, stop_midi = true_midi_pairs[1]

            divisions = additional_pairs_needed + 1
            for i in range(divisions):
                progress = i / divisions
                true = start_true + (stop_true - start_true) * progress
                midi = start_midi + (stop_midi - start_midi) * progress
                yield true, midi

            yield from true_midi_pairs[1:]

    def set_note_from_pairs(self, midi_note, true_midi_pairs):
        true_midi_pairs = list(self._padded_pairs(true_midi_pairs))

        self._true_vels[midi_note, 1::2] = next(zip(*true_midi_pairs[1:-1]))

        for i in range(len(true_midi_pairs) - 1):
            start_true, start_midi = true_midi_pairs[i]
            stop_true, stop_midi = true_midi_pairs[i+1]

            a = (stop_midi - start_midi) / (stop_true - start_true)
            b = start_midi - start_true * a

            self._gradients_and_intercepts[midi_note, i*2] = a, b


class _VelCurveFactoryBase:
    def __call__(self):
        vel_curve = self._make_vel_curve()

        for midi_note, pairs_for_notes in enumerate(self._pairs_for_notes):
            if len(pairs_for_notes) < 2:
                raise CurvesError(
                    f"note {midi_note} should contain at least 2 pairs"
                )

            vel_curve.set_note_from_pairs(midi_note, pairs_for_notes)

        return vel_curve

    def add_pair(self, midi_note, new_in, new_out):
        pairs = self._pairs_for_notes[midi_note]

        for i, (in_, out) in enumerate(pairs):
            if new_in == in_:
                pairs[i] = (new_in, new_out)
                return
            elif new_in < in_:
                pairs.insert(i, (new_in, new_out))
                return

        pairs.append((new_in, new_out))

    def add_pair_for_all_notes(self, new_in, new_out):
        for midi_note in range(128):
            self.add_pair(midi_note, new_in, new_out)


class MidiToTrueVelCurveFactory(_VelCurveFactoryBase):
    _make_vel_curve = MidiToTrueVelCurve.empty

    def __init__(self):
        self._pairs_for_notes = [[(1, 0.5), (127, 0.5)] for _ in range(128)]

    def add_pair_for_white_notes(self, new_in, new_out):
        for midi_note in range(128):
            if midi_note % 12 in [0, 2, 4, 5, 7, 9, 11]:
                self.add_pair(midi_note, new_in, new_out)

    def add_pair_for_black_notes(self, new_in, new_out):
        for midi_note in range(128):
            if midi_note % 12 in [1, 3, 6, 8, 10]:
                self.add_pair(midi_note, new_in, new_out)


class TrueToMidiVelCurveFactory(_VelCurveFactoryBase):
    def __init__(self):
        self._pairs_for_notes = [[(0.1, 64), (1.0, 64)] for _ in range(128)]

    def _make_vel_curve(self):
        most_pairs_needed = max(len(pairs) for pairs in self._pairs_for_notes)
        comparisons = (most_pairs_needed - 2).bit_length()
        return TrueToMidiVelCurve(comparisons=comparisons)
