class Task:
    def __init__(self, no: int, wcet, period, mem_req, mem_active_ratio, cpu):
        self.wcet = wcet
        self.period = self.deadline = period
        self.memory_req = mem_req
        self.memory_active_ratio = mem_active_ratio
        self.no = no

        self.cpu = cpu
        self.cpu_frequency = None
        self.memory = None

        self.det = 0
        self.det_remain = 0
        self.det_old = None
        self.det_remain_old = None

        self.period_start = 0
        self.prev_exec_time = None

    def __lt__(self, other):
        return self.no < other.no

    def calc_priority(self) -> float:
        # min heap 사용을 위해 역수로 계산.
        return float(self.deadline)/self.det_remain

    def calc_det(self):
        new_det = self.wcet / min(self.cpu_frequency.wcet_scale, self.memory.wcet_scale)

        self.det_old = self.det
        self.det = int(round(new_det))
        if self.det == 0:
            self.det = 1

        self.det_remain_old = self.det_remain
        if not self.det_remain:
            self.det_remain = self.det
        elif self.det_remain > 0 & self.det != self.det_old:
            self.det_remain = int(round(self.det_remain * (new_det / self.det_old)))

    def revert_det(self):
        self.det = self.det_old
        self.det_remain = self.det_remain_old

    def desc_task(self) -> str:
        return (f'    [no:{self.no}, wcet:{self.wcet}, period:{self.period}, ' +
                f'cpu_freq(scale):{self.cpu_frequency.wcet_scale}, memory:{self.memory.type}, ' +
                f'det:{self.det}, det_remain:{self.det_remain}, deadline:{self.deadline}]')

    def check_task(self):
        if self.det == 0:
            raise Exception(self.desc_task()+": zero det.")
        if self.det < self.det_remain:
            raise Exception(self.desc_task() + ": invalid det.")
        if self.deadline < 0:
            raise Exception(self.desc_task() + ": negative deadline")
        return True

    def revoke_memory(self):
        self.memory.used_capacity -= self.memory_req
        self.memory = None

    def exec_idle(self, time: int, update_deadline: bool):
        self.memory.power_consumed_idle += time * self.memory_req * self.memory.power_idle
        if update_deadline:
            self.deadline -= 1

    def exec_active(self, time: int, system):
        if not self.prev_exec_time:
            pass
        elif self.prev_exec_time != system.time - 1:
            # 새로 수행되는 태스크일 때만 cpu와 메모리 다시 할당
            system.reassign_task(self)

        self.prev_exec_time = system.time
        self.deadline -= time
        self.det_remain -= time

        # calc power
        wcet_scaled_cpu = 1 / self.cpu_frequency.wcet_scale
        wcet_scaled_mem = 1 / self.memory.wcet_scale
        wcet_scaled = wcet_scaled_cpu + wcet_scaled_mem

        self.cpu.add_power_consumed_active(time * self.cpu_frequency.power_active * wcet_scaled_cpu / wcet_scaled)
        self.cpu.add_power_consumed_idle(time * self.cpu_frequency.power_idle * wcet_scaled_mem / wcet_scaled)
        self.memory.add_power_consumed_active(
            time * self.memory.power_active * self.memory_req * self.memory_active_ratio)
        self.memory.add_power_consumed_idle(
            time * self.memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

        # print
        if system.verbose != system.V_NO:
            print(f'{system.time}부터 {system.time + 1}까지 task {self.no} 실행 '
                  f'(cpu_freq:{self.cpu_frequency.wcet_scale}, '
                  f'memory_type:{self.memory.get_type_str()})')
