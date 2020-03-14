import math


class RTTask:
    total_power = 0
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
        self.det = wcet
        self.exec_mode = 'O'  # 'O'(Original) 혹은 'G'(GA)로 현재 실행모드를 저장함.
        self.exec_mode_num = None

        # PD2 알고리즘을 위해 유지하는 정보.
        # i가 변경될 때만 새로 계산해주면 됨.
        self.i_job = self.d = self.b = self.D = None

        # 시뮬레이션을 위해 유지하는 정보
        self.k = 0
        self.deadline = None  # 이번 주기의 데드라인을 시간에 대한 절대적 값으로 저장
        self.next_period_start = 0  # 다음 주기의 시작을 저장

    def desc_task(self) -> str:
        return (f'    [type:RT, no:{self.no}, wcet:{self.wcet}, period:{self.period}, ' +
                f'det:{self.det}, i_job:{self.i_job}, exec_mode:{self.exec_mode}, deadline:{self.deadline}, ' +
                "d:{}, D:{}, b:{}]".format(self.d, self.D, self.b))

    def __lt__(self, other):
        if self.d == other.d:
            if self.b == other.b == 1:
                return self.D >= other.D
            return self.b > other.b
        return self.d < other.d

    def set_exec_mode(self, mode, mode_num, processor, memories):
        if mode == 'G':
            if self.exec_mode == 'O':
                new_processor_mode = processor.modes[self.ga_processor_mode[mode_num]]
                new_memory = memories.list[self.ga_memory_mode[mode_num]]

                det_executed = self.i_job + 1
                det_remain = self.det - det_executed
                changed_det_remain = det_remain / min(new_processor_mode.wcet_scale, new_memory.wcet_scale)
                self.det = round(det_executed + changed_det_remain)

            elif self.exec_mode_num != mode_num:
                pre_processor_mode = processor.modes[self.ga_processor_mode[self.exec_mode_num]]
                pre_memory = memories.list[self.ga_memory_mode[self.exec_mode_num]]
                new_processor_mode = processor.modes[self.ga_processor_mode[mode_num]]
                new_memory = memories.list[self.ga_memory_mode[mode_num]]

                det_executed = self.i_job + 1
                det_remain = self.det - det_executed
                changed_det_remain = det_remain * min(pre_processor_mode.wcet_scale, pre_memory.wcet_scale) \
                                     / min(new_processor_mode.wcet_scale, new_memory.wcet_scale)
                self.det = round(det_executed + changed_det_remain)

        else:  # mode == 'O'
            if not self.exec_mode or self.i_job == 1:
                self.det = self.wcet

            elif self.exec_mode == 'G':
                pre_processor_mode = processor.modes[self.ga_processor_mode[self.exec_mode_num]]
                pre_memory = memories.list[self.ga_memory_mode[self.exec_mode_num]]

                det_executed = self.i_job + 1
                det_remain = self.det - det_executed
                changed_det_remain = det_remain * min(pre_processor_mode.wcet_scale, pre_memory.wcet_scale)
                self.det = round(det_executed + changed_det_remain)

        self.exec_mode = mode
        if mode_num != 'O':
            self.exec_mode_num = mode_num

        # task의 weight이 변경되었으므로 다시 계산해야함.
        self.calc_d_for_pd2()
        self.calc_D_for_pd2()
        self.calc_b_for_pd2()

    def set_job(self):
        # run 하기 전 한번만 실행됨
        self.i_job = 1
        self.deadline = self.next_period_start = self.period

    def init_job(self):
        # 매 주기의 시작에 실행됨(매 job 마다 실행됨)
        self.i_job = 1
        self.next_period_start = self.deadline
        self.deadline += self.period
        self.k += 1

        self.exec_mode = 'O'
        self.det = self.wcet

    def calc_d_for_pd2(self):
        self.d = math.ceil((self.k * self.det + self.i_job) / (self.det / self.period))

    def calc_b_for_pd2(self):
        if abs(self.d - (self.k * self.det + self.i_job) / (self.det / self.period)) <= RTTask.EPS:
            self.b = 0
        self.b = 1

    def calc_D_for_pd2(self):
        self.D = math.ceil(math.ceil(math.ceil(self.d) * (1 - self.det / self.period)) / (1 - self.det / self.period))

    def is_deadline_violated(self, cur_time):
        if self.deadline <= cur_time:
            raise Exception(self.desc_task() + ": deadline failure")
        return True

    def is_finish(self):
        return self.i_job >= self.det + 1

    def exec_idle(self, processor, memories, quantum=1):
        memory = memories.list[0] if self.exec_mode == 'O' else memories.list[self.ga_memory_mode[self.exec_mode_num]]
        power_consumed = quantum * self.memory_req * memory.power_idle
        memory.power_consumed_idle += power_consumed
        RTTask.total_power += power_consumed

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

            RTTask.total_power += quantum * 0.5 * (processor_mode.power_idle + processor_mode.power_idle)
            RTTask.total_power += quantum * memory.power_idle * self.memory_req

        else:  # self.exec_mode == 'G'
            processor_mode = processor.modes[self.ga_processor_mode[self.exec_mode_num]]
            memory = memories.list[self.ga_memory_mode[self.exec_mode_num]]

            wcet_scaled_cpu = 1 / processor_mode.wcet_scale
            wcet_scaled_mem = 1 / memory.wcet_scale
            wcet_scaled = wcet_scaled_cpu + wcet_scaled_mem

            # Processor
            processor.add_power_consumed_active(quantum * processor_mode.power_active * wcet_scaled_cpu / wcet_scaled)
            processor.add_power_consumed_idle(quantum * processor_mode.power_idle * wcet_scaled_mem / wcet_scaled)

            # Memory
            memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
            memory.add_power_consumed_idle(
                quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

            RTTask.total_power += quantum * processor_mode.power_active * wcet_scaled
            RTTask.total_power += quantum * memory.power_active * self.memory_req

        self.i_job += quantum
        # i 변경되었으므로, b, d, D를 다시 계산
        self.calc_d_for_pd2()
        self.calc_b_for_pd2()
        self.calc_D_for_pd2()


class NonRTTask:
    total_power = 0

    def __init__(self, no, at, bt, mem_req, mem_active_ratio):
        # 태스크 정보
        self.no = no
        self.at = at
        self.bt = bt
        self.memory_req = mem_req
        self.memory_active_ratio = mem_active_ratio

        # 저전력 모드를 위해 유지하는 정보.
        self.det = bt
        self.exec_mode = 'O' # 'O' or 'DH'

        # 시뮬레이션 및 결과 출력을 위해 유지하는 정보
        self.exec_time = 0
        self.start_time = None
        self.end_time = None

    def set_exec_mode(self, mode, processor, memories):
        processor_mode = processor.modes[-1]
        memory = memories.list[-1]

        if self.exec_mode == 'O' and mode == 'DH':
            bt_remain = self.det - self.exec_time
            changed_bt_remain = bt_remain / min(processor_mode.wcet_scale, memory.wcet_scale)
            self.det = round(self.exec_time + changed_bt_remain)

        if self.exec_mode == 'DH' and mode == 'O':
            bt_remain = self.det - self.exec_time
            changed_bt_remain = bt_remain * min(processor_mode.wcet_scale, memory.wcet_scale)
            self.det = round(self.exec_time + changed_bt_remain)

        self.exec_mode = mode

    def desc_task(self) -> str:
        return (f'    [type:None-RT, no:{self.no}, at:{self.at}, bt:{self.bt}, ' +
                f'exec_time:{self.exec_time}, start_time:{self.start_time}]')

    def exec_active(self, processor, memories, cur_time, quantum=1):
        if self.exec_mode == 'O':
            processor_mode = processor.modes[0]
            processor.add_power_consumed_active(quantum * processor_mode.power_active * 0.5)
            processor.add_power_consumed_idle(quantum * processor_mode.power_idle * 0.5)

            memory = memories.list[0]
            memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
            memory.add_power_consumed_idle(quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

            NonRTTask.total_power += quantum * 0.5 * (processor_mode.power_active + processor_mode.power_idle)
            NonRTTask.total_power += quantum * memory.power_active * self.memory_req

        else:
            processor_mode = processor.modes[-1]
            memory = memories.list[-1]

            wcet_scaled_cpu = 1 / processor_mode.wcet_scale
            wcet_scaled_mem = 1 / memory.wcet_scale
            wcet_scaled = wcet_scaled_cpu + wcet_scaled_mem

            # Processor
            processor.add_power_consumed_active(quantum * processor_mode.power_active * wcet_scaled_cpu / wcet_scaled)
            processor.add_power_consumed_idle(quantum * processor_mode.power_idle * wcet_scaled_mem / wcet_scaled)

            # Memory
            memory.add_power_consumed_active(quantum * memory.power_active * self.memory_req * self.memory_active_ratio)
            memory.add_power_consumed_idle(
                quantum * memory.power_idle * self.memory_req * (1 - self.memory_active_ratio))

            NonRTTask.total_power += quantum * processor_mode.power_active * wcet_scaled
            NonRTTask.total_power += quantum * memory.power_active * self.memory_req

        if not self.start_time:
            self.start_time = cur_time
        self.exec_time += quantum

    def exec_idle(self, memories, quantum=1):
        memory = memories.list[0] if self.exec_mode == 'O' else memories.list[-1]
        power_consumed = quantum * self.memory_req * memory.power_idle
        memory.power_consumed_idle += power_consumed
        NonRTTask.total_power += power_consumed

    def is_end(self):
        return self.exec_time == self.bt


