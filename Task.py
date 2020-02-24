class RTTask:
    def __init__(self, no, wcet, period, mem_req, mem_active_ratio):
        # 태스크 정보
        self.no = no
        self.wcet = wcet
        self.period = period
        self.memory_req = mem_req
        self.memory_active_ratio = mem_active_ratio

        # ga의 결과로 할당된 모드 정보를 저장.
        self.ga_processor_mode = None
        self.ga_memory_mode = None

        # 시뮬레이션을 위해 유지하는 정보
        self.wcet_remain = wcet
        self.relative_deadline = period
        self.next_period_start = 0

    def exec_idle_with_original(self, memories, quantum, update_deadline):
        # 오리지널 자원을 이용하여 quantum 만큼 task를 idle로 실행
        memory = memories[0]  # DRAM
        memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle
        if update_deadline:
            self.deadline -= quantum

    def exec_idle_with_ga(self, memories, quantum, update_deadline):
        # ga의 결과로 할당된 자원을 이용하여 quantum 만큼 task를 idle로 실행
        memory = memories[self.ga_memory_mode]
        memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle
        if update_deadline:
            self.deadline -= quantum

    def exec_active_with_original(self, processor, memories, quantum):
        # 오리지널 자원을 이용하여 quantum 만큼 task를 active로 실행
        # Processor
        processor_mode = processor.modes[0]
        processor.add_power_consumed_active(quantum * processor_mode.power_active * 0.5)
        processor.add_power_consumed_idle(quantum * processor_mode.power_idle * 0.5)

        # Memory
        memory = memories[0]
        memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
        memory.add_power_consumed_idle(quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

        self.wcet_remain -= quantum
        self.relative_deadline -= quantum

    def exec_active_with_ga(self, processor, memories, quantum):
        # GA의 결과로 할당받은 자원을 이용하여 quantum 만큼 task를 active로 실행
        processor_mode = processor.modes[self.ga_processor_mode]
        memory = memories[self.ga_memory_mode]

        wcet_scaled_cpu = 1 / processor_mode.wcet_scale
        wcet_scaled_mem = 1 / memory.wcet_scale
        wcet_scaled = wcet_scaled_cpu + wcet_scaled_mem

        # Processor
        processor.add_power_consumed_active(quantum * processor_mode.power_active * wcet_scaled_cpu / wcet_scaled)
        processor.add_power_consumed_idle(quantum * processor_mode.power_idle * wcet_scaled_mem / wcet_scaled)

        # Memory
        memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
        memory.add_power_consumed_idle(quantum * memory.power_idle * self.memory_req * self.memory_active_ratio)

        self.deadline -= quantum
        self.det_remain -= quantum * min(processor_mode.wcet_scale, memory.wcet_scale)


class NonRTTask:
    def __init__(self, no, at, bt):
        # 태스크 정
        self.no = no
        self.at = at
        self.bt = bt
        self.memory_req = None
        self.memory_active_ratio = None

        # 시뮬레이션 및 결과 출력을 위해 유지하는 정보
        self.bt_remain = bt
        self.start_time = None
        self.end_time = None

    def exec_active(self, processor, memories, quantum, cur_time):
        # Non-RT-Task는 항상 Original로 실행
        if not self.start_time:
            self.start_time = cur_time
        self.bt_remain -= quantum

    def is_end(self):
        return self.bt_remain == 0
