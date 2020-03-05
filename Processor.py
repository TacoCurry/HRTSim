class ProcessorMode:
    def __init__(self, wcet_scale, power_active, power_idle):
        self.wcet_scale = wcet_scale
        self.power_active = power_active
        self.power_idle = power_idle


class Processor:
    def __init__(self, n_core):
        self.n_core = n_core

        self.modes = []

        self.power_consumed_idle = 0
        self.power_consumed_active = 0

    def insert_processor_mode(self, wcet_scale, power_active, power_idle):
        self.modes.append(ProcessorMode(wcet_scale, power_active, power_idle))

    def exec_idle_with_dvfs(self, quantum=1):
        self.power_consumed_idle += quantum * self.modes[-1].power_idle

    def exec_idle_without_dvfs(self, quantum=1):
        self.power_consumed_idle += quantum * self.modes[0].power_idle

    def add_power_consumed_idle(self, power):
        self.power_consumed_idle += power

    def add_power_consumed_active(self, power):
        self.power_consumed_active += power

    def init(self):
        self.power_consumed_idle = 0
        self.power_consumed_active = 0
