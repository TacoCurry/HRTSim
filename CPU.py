from abc import *


class CpuFrequency:
    def __init__(self, wcet_scale, power_active, power_idle):
        self.wcet_scale = wcet_scale
        self.power_active = power_active
        self.power_idle = power_idle

    def __lt__(self, other):
        return self.wcet_scale > other.wcet_scale


class CPU(metaclass=ABCMeta):
    MAX_CPU_FREQUENCIES = 15

    def __init__(self):
        self.n_core = None

        self.frequencies = []
        self.n_frequencies = 0

        self.power_consumed_idle = 0
        self.power_consumed_active = 0

    def insert_cpu_frequency(self, wcet_scale: float, power_active: float, power_idle: float) -> bool:
        if self.n_frequencies >= CPU.MAX_CPU_FREQUENCIES:
            return False

        self.frequencies.append(CpuFrequency(wcet_scale, power_active, power_idle))
        self.n_frequencies += 1

        self.frequencies.sort()
        return True

    def assign_cpu_frequency(self, task):
        # 첫 할당에는 DVFS를 하지 않는 것(wcet_scale=1)로 할당합니다.
        task.cpu_frequency = self.frequencies[0]

    @abstractmethod
    def reassign_cpu_frequency(self, task, system) -> bool:
        pass

    def exec_idle(self, time: int):
        self.power_consumed_idle += time * self.frequencies[-1].power_idle

    def add_power_consumed_idle(self, power: float):
        self.power_consumed_idle += power

    def add_power_consumed_active(self, power: float):
        self.power_consumed_active += power


class NoneDVFSCPU(CPU):
    def reassign_cpu_frequency(self, task, system) -> bool:
        return True


class DVFSCPU(CPU):
    def reassign_cpu_frequency(self, task, system) -> bool:
        for i in range(self.n_frequencies):
            task.cpu_frequency = self.frequencies[self.n_frequencies - 1 - i]
            task.calc_det()
            if system.is_schedule(task):
                return True
            task.revert_det()
        return False
