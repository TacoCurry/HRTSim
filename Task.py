class RTTask:
    EPS = 1e-6  # 부동 소수점 비교 연산을 위해 사용

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

        # DVFS 및 HM의 적용으로 변화하는 wcet를 저장함.
        self.det = self.wcet
        self.det_mode = 'O'
        # 'O'(Original) 혹은 'G'(GA)로 현재 det가 어느 모드로 계산되어있는지 저장해서 계산을 줄

        # PD2 알고리즘을 위해 유지하는 정보.
        # i가 변경될 때만 새로 계산해주면 됨.
        self.i = self.d = self.b = self.D = None

        # 시뮬레이션을 위해 유지하는 정보
        self.deadline = None  # 이번 주기의 데드라인을 시간에 대한 절대적 값으로 저장
        self.next_period_start = 0  # 다음 주기의 시작을 저장

    def __lt__(self, other):
        # PD2 우선순위 구
        pass

    def init_job(self):
        # 매 주기의 시작에 실행됨(매 job 마다 실행됨)
        self.det = self.wcet
        self.det_mode = 'O'

        self.i = 1
        self.calc_d_for_pd2()
        self.calc_D_for_pd2()
        self.calc_b_for_pd2()

        self.deadline = self.next_period_start
        self.next_period_start += self.period

    def calc_d_for_pd2(self):
        # TODO PD2에서 사용되는 d 계산하는 식 필요
        pass

    def calc_b_for_pd2(self):
        # TODO PD2에서 사용되는 b 계산하는 식 필요
        pass

    def calc_D_for_pd2(self):
        # TODO PD2에서 사용되는 D 계산하는 식 필요
        pass

    def is_deadline_violated(self, cur_time):
        return self.deadline <= cur_time

    def is_finish(self):
        return self.i >= self.det + 1

    def exec_idle_with_original(self, memories, quantum=1):
        # 오리지널 자원을 이용하여 quantum 만큼 task를 idle로 실행
        memory = memories[0]  # DRAM
        memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle

    def exec_idle_with_ga(self, memories, quantum=1):
        # ga의 결과로 할당된 자원을 이용하여 quantum 만큼 task를 idle로 실행
        memory = memories[self.ga_memory_mode]
        memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle

    def exec_active_with_original(self, processor, memories, quantum=1):
        # 오리지널 자원을 이용하여 quantum 만큼 task를 active로 실행
        # Processor
        processor_mode = processor.modes[0]
        processor.add_power_consumed_active(quantum * processor_mode.power_active * 0.5)
        processor.add_power_consumed_idle(quantum * processor_mode.power_idle * 0.5)

        # Memory
        memory = memories[0]
        memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
        memory.add_power_consumed_idle(quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

        if self.det_mode == 'G':
            self.det_mode = 'O'
            # TODO 오리지널 따라 det를 다시 계산하는 코드 필요!

        self.i += quantum
        # i와 det 변경되었으므로, b, d, D를 다시 계산
        self.calc_b_for_pd2()
        self.calc_D_for_pd2()
        self.calc_d_for_pd2()

    def exec_active_with_ga(self, processor, memories, quantum=1):
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

        if self.det_mode == 'O':
            self.det_mode = 'G'
            # TODO ga로 할당된 결과에 따라 det를 다시 계산하는 코드 필요!

        self.i += quantum
        # i와 det 변경되었으므로, b, d, D를 다시 계산
        self.calc_b_for_pd2()
        self.calc_D_for_pd2()
        self.calc_d_for_pd2()


class NonRTTask:
    def __init__(self, no, at, bt):
        # 태스크 정보
        self.no = no
        self.at = at
        self.bt = bt
        self.memory_req = None
        self.memory_active_ratio = None

        # 시뮬레이션 및 결과 출력을 위해 유지하는 정보
        self.exec_time = 0
        self.start_time = None
        self.end_time = None

    def exec_active(self, processor, memories, quantum, cur_time):
        # Non-RT-Task는 항상 Original로 실행

        # TODO 실행 시 전력 소모 저장하는 코드 필요!

        if not self.start_time:
            self.start_time = cur_time
        self.exec_time += quantum

    def exec_idle(self, processor, memories, quantum, cur_time):
        # TODO 실행 시 전력 소모 저장하는 코드 필요!
        pass

    def is_end(self):
        return self.exec_time == self.bt
