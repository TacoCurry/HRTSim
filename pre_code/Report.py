class Report:
    def __init__(self, system):
        system.memories.calc_total_power_consumed()

        power_consumed_cpu = system.CPU.power_consumed_active + system.CPU.power_consumed_idle
        power_consumed_mem = system.memories.total_power_consumed_active + system.memories.total_power_consumed_idle
        power_consumed_active = system.CPU.power_consumed_active + system.memories.total_power_consumed_active
        power_consumed_idle = system.CPU.power_consumed_idle + system.memories.total_power_consumed_idle
        power_consumed = power_consumed_cpu + power_consumed_mem

        self.system = system
        self.power_consumed_avg = power_consumed / system.time
        self.power_consumed_cpu_avg = power_consumed_cpu / system.time
        self.power_consumed_mem_avg = power_consumed_mem / system.time
        self.power_consumed_active_avg = power_consumed_active / system.time
        self.power_consumed_idle_avg = power_consumed_idle / system.time
        self.utilization = float(system.sum_utils) / system.n_utils / system.CPU.n_core * 100

    def print_console(self):
        print(f'\nnum of core: {self.system.CPU.n_core}')
        print(f'policy: {self.system.name}')
        print(f'simulation time: {self.system.time}')
        print(f'average power consumed: {round(self.power_consumed_avg, 3)}')
        print(f'CPU + MEM power consumed: {round(self.power_consumed_cpu_avg, 3)} + {round(self.power_consumed_mem_avg, 3)}')
        print(f'ACTIVE + IDLE power consumed: '
              f'{round(self.power_consumed_active_avg, 3)} + {round(self.power_consumed_idle_avg, 3)}')
        print(f'utilization: {round(self.utilization, 3)}%')
