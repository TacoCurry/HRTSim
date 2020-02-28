import math


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
        self.det = None
        self.exec_mode = None  # 'O'(Original) 혹은 'G'(GA)로 현재 실행모드를 저장함.

        # PD2 알고리즘을 위해 유지하는 정보.
        # i가 변경될 때만 새로 계산해주면 됨.
        self.i = self.d = self.b = self.D = None

        # 시뮬레이션을 위해 유지하는 정보
        self.deadline = None  # 이번 주기의 데드라인을 시간에 대한 절대적 값으로 저장
        self.next_period_start = 0  # 다음 주기의 시작을 저장

    # 변수 반환 디버그용
    def desc_task(self) -> str:
        return (f'    [no:{self.no}, wcet:{self.wcet}, period:{self.period}, ' +
                f'det:{self.det}, det_mode:{self.det_mode}, deadline:{self.deadline}]')

    def __lt__(self, other):
        if self.d == other.d:
            if self.b == other.b == 1:
                return self.D >= other.D
            return self.b > other.b
        return self.d < other.d

    def set_exec_mode(self, mode, processor, memories):
        # 'G(GA)' 혹은 'O(Original)'로 실행 모드를 변경하고 det도 다시 계산.
        processor_mode = processor[self.ga_processor_mode]
        memory = memories.list[self.ga_memory_mode]

        if mode == 'G':
            if not self.exec_mode or self.i == 1:
                self.det = self.wcet / min(processor_mode.wcet_scale, memory.wcet_scale)

            if self.exec_mode == 'O':
                det_executed = self.i + 1
                det_remain = self.det - det_executed
                changed_det_remain = det_remain / min(processor_mode.wcet_scale, memory.wcet_scale)
                self.det = round(det_executed + changed_det_remain)

        else:  # mode == 'O'
            if not self.exec_mode or self.i == 1:
                self.det = self.wcet

            if self.exec_mode == 'G':
                det_executed = self.i + 1
                det_remain = self.det - det_executed
                changed_det_remain = det_remain * min(processor_mode.wcet_scale, memory.wcet_scale)
                self.det = round(det_executed + changed_det_remain)

        self.exec_mode = mode

        # task의 weight이 변경되었으므로 다시 계산해야함.
        self.calc_d_for_pd2()
        self.calc_D_for_pd2()
        self.calc_b_for_pd2()

    def init_job(self):
        # 매 주기의 시작에 실행됨(매 job 마다 실행됨)
        self.i = 1
        self.deadline = self.next_period_start
        self.next_period_start += self.period


    def calc_d_for_pd2(self):
        self.d = math.ceil(self.i / (self.det / self.period))

    def calc_b_for_pd2(self):
        if abs(self.d - self.i / (self.det / self.period)) <= RTTask.EPS:
            return 0
        return 1

    def calc_D_for_pd2(self):
        self.D = math.ceil(math.ceil(math.ceil(self.d) * (1 - self.det / self.period)) / (1 - self.det / self.period))

    def is_deadline_violated(self, cur_time):
        if self.deadline <= cur_time:
            raise Exception(self.desc_task() + ": deadline failure")
        return True

    def is_finish(self):
        return self.i >= self.det + 1

    def exec_idle(self, memories, quantum=1):
        if self.exec_mode == 'O':
            # 오리지널 자원을 이용하여 quantum 만큼 task를 idle로 실행
            memory = memories.list[0]  # DRAM
            memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle
        else:  # exec_mode == 'G'
            # ga의 결과로 할당된 자원을 이용하여 quantum 만큼 task를 idle로 실행
            memory = memories.list[self.ga_memory_mode]
            memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle

    def exec_active(self, processor, memories, quantum=1):
        if self.exec_mode == 'O':
            # 오리지널 자원을 이용하여 quantum 만큼 task를 active로 실행
            processor_mode = processor.modes[0]
            processor.add_power_consumed_active(quantum * processor_mode.power_active * 0.5)
            processor.add_power_consumed_idle(quantum * processor_mode.power_idle * 0.5)

            memory = memories.list[0]
            memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
            memory.add_power_consumed_idle(
                quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

        else:  # self.exec_mode == 'G'
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

        self.i += quantum
        # i 변경되었으므로, b, d, D를 다시 계산
        self.calc_d_for_pd2()
        self.calc_b_for_pd2()
        self.calc_D_for_pd2()




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
        processor_mode = processor.modes[0]
        processor.add_power_consumed_active(quantum * processor_mode.power_active * 0.5)
        processor.add_power_consumed_idle(quantum * processor_mode.power_idle * 0.5)

        memory = memories.list[0]
        memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
        memory.add_power_consumed_idle(quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

        if not self.start_time:
            self.start_time = cur_time
        self.exec_time += quantum

    def exec_idle(self, memories, quantum):
        # Non-RT-Task는 항상 Original로 실행
        memory = memories.list[0]  # DRAM
        memory.power_consumed_idle += quantum * self.memory_req * memory.power_idle

    def is_end(self):
        return self.exec_time == self.bt
