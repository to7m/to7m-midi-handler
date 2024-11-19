from ._scanner import Scanner
from ._watcher import Watcher
from ._resources import ResourceClaimFailError, Resources


class _ConnectionsChanged(Exception):
    pass


class _VerificationFailed(Exception):
    pass


class _LcpManager:
    def __init__(
        self, lcp_i, controllers_profile_spec, ports_to_lcp_queue, connections
    ):
        self.lcp_i = lcp_i
        self.controllers_profile_spec = controllers_profile_spec
        self.ports_to_lcp_queue = ports_to_lcp_queue
        self.connections = connections

    def send_internal_to_lcp(self, msg):
        self.ports_to_lcp_queue.put((0, msg))


class _LsmpManager:
    ...


class _Managers:
    def __init__(self):
        self._list = []
        self._dict = {}

    def __iter__(self):
        for loaded_profile_i, item in enumerate(self._list):
            if item:
                profile_spec, manager = item
                yield loaded_profile_i, profile_spec, manager

    def __getitem__(self, profile):
        return self._dict[profile]

    def add(self, profile_spec, manager):
        loaded_profile_i = len(self._list)
        self._list.append((profile_spec, manager))

        if profile_spec not in self._dict:
            self._dict[profile_spec] = []

        self._dict[profile_spec].append((loaded_profile_i, manager))

    def add_none(self):
        self._list.append(None)

    def copy(self):
        inst = type(self)()

        for loaded_profile_i, item in enumerate(self._list):
            if item is None:
                inst.add_none()
            else:
                profile_spec, manager = item
                inst.add(profile_spec, manager)

        return inst


class ConnectionsManager:
    def __init__(
        self,
        controllers_profile_specs, sound_modules_profile_specs,
        send_to_core
    ):
        self._controllers_profile_specs = controllers_profile_specs
        self._sound_modules_profile_specs = sound_modules_profile_specs
        self._send_to_core = send_to_core

        self._scanner = Scanner()

        self._lcp_managers = _Managers()
        self._lsmp_managers = _Managers()

        self._processed_external_state = None
        self._unclaimed_resources = None
        self._target_lcp_counts = None
        self._target_lsmps = None

    def _verify_lcp(self, lcp_manager):
        +"this needs to check both OS connections and internal"

        


    def _unload_faulty_lcps(self):
        for lcp_i, _, lcp_manager in self._lcp_managers:
            try:
                self._verify_lcp(lcp_manager)
            except _VerificationFailed:
                self._disconnect_lcp(lcp_manager)

    def _unload_faulty_lsmps(self):
        old_lsmp_mans

    def _get_target_lcp_count(self, connect_specs):
        count = 0
        while True:
            unclaimed_resources = self._unclaimed_resources.copy()

            try:
                unclaimed_resources.claim(connect_specs)
            except ResourceClaimFailError:
                return count
            else:
                self._unclaimed_resources = unclaimed_resources
                count += 1

    def _set_target_lcp_counts(self):
        self._target_lcp_counts = {
            cp_spec: self._get_target_lcp_count(cp_spec.connect_specs)
            for cp_spec in self._controllers_profile_specs
        }

    def _get_is_lscp_target(self, connect_specs):
        unclaimed_resources = self._unclaimed_resources.copy()

        try:
            unclaimed_resources.claim(connect_specs)
        except ResourceClaimFailError:
            return False
        else:
            self._unclaimed_resources = unclaimed_resources
            return True

    def _set_target_lsmps(self):
        self._target_lsmps = {
            smp_spec: self._get_is_lscp_target(smp_spec.connect_specs)
            for smp_spec in self._sound_modules_profile_specs
        }

    def _try_unload_an_excess_lcp(self):
        for controllers_profile_spec in self._controllers_profile_specs:
            current_lcps = self._lcps_for_controllers_profiles[
                controllers_profile_spec
            ]
            target_lcp_count = self._target_lcp_counts[
                      controllers_profile_spec
                  ]

            if len(current_lcps) > target_lcp_count:
                manager = current_lcps[-1]
                manager.disconnect_and_unload()
                raise _ConnectionsChanged

    def _try_unload_an_excess_lsmp(self):
        for sound_modules_profile_spec in self._sound_modules_profile_specs:
            if not self._lsmps_for_sound_modules_profiles[
                sound_modules_profile_spec
            ]:
                continue

            if sound_modules_profile_spec not in self._target_lsmps:
                continue

            manager.disconnect_and_unload()
            raise _ConnectionsChanged

    def _make_lcp(self, profile_spec):
        ports_to_lcp_queue = profile_spec.instantiator()

        manager = _LcpManager(
            lcp_i, controllers_profile_spec, ports_to_lcp_queue, connections
        )

    def _try_make_a_new_lcp(self):
        for controllers_profile_spec in self._controllers_profile_specs:
            current = self._lcp_managers[controllers_profile_spec]
            target_count = self._target_lcp_counts[controllers_profile_spec]

            if target_count > len(current):
                self._make_lcp(controllers_profile_spec)

    def _try_make_a_new_lsmp(self):
        for sound_modules_profile_spec in self._sound_modules_profile_specs:


    def _try_change_connections(self):
        self._unload_faulty_lcps()
        self._unload_faulty_lsmps()

        self._unclaimed_resources = Resources.from_processed_external_state(
            self._processed_external_state
        )
        self._set_target_lcp_counts()
        self._set_target_lsmps()

        self._try_unload_an_excess_lcp()
        self._try_unload_an_excess_lsmp()

        for list_ in self._lcp_managers, self._lsmp_managers:
            self._remove_trailing_nones(list_)

        self._try_make_a_new_lcp()
        self._try_make_a_new_lsmp()

    def _scan_and_update(self):
        while True:
            results_changed, self._processed_external_state \
                = self._scanner.scan()

            if results_changed:
                try:
                    self._try_change_connections()
                except _ConnectionsChanged:
                    pass
            else:
                break

    def run(self):
        with Watcher() as watcher:
            while True:
                self._scan_and_update()
                watcher.wait_for_events()
