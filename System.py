from abc import *
from CPU import NoneDVFSCPU, DVFSCPU
from Memory import Memory
import heapq
import sys
from Input import InputUtils
from Report import Report


class System(metaclass=ABCMeta):
    """super class of all POLICYs"""
    V_NO = 0
    V_SIMPLE = 1
    V_DETAIL = 2

    def __init__(self, end_sim_time: int, verbose: int):
        self.name = None
        self.desc = None

        self.CPU = None
        self.memories = None

        self.time = 0
        self.end_sim_time = end_sim_time
        self.verbose = verbose

        self.tasks = []
        self.wait_period_queue = []
        self.queue = []

        self.sum_utils = 0
        self.n_utils = 0

    def run(self):
        # Set input files
        InputUtils.set_processor(self)
        InputUtils.set_memory(self)
        InputUtils.set_tasks(self)
        self.setup_tasks()

        # Run simulator...
        while self.time < self.end_sim_time:
            if self.verbose == System.V_DETAIL:
                print(f'\ntime = {self.time}')
                self.print_queue()

            # time 부터 (time+1)동안 실행될 task 코어의 개수만큼 고르기.
            exec_task_list = []
            if len(self.queue) < self.CPU.n_core:
                # 큐에 있는 것 모두 실행가능(코어의 개수보다 적으므로)
                for tup in self.queue:
                    exec_task_list.append(tup[1])
                self.queue = []

                # self.CPU.n_core - len(self.queue)개의 코어는 idle로 실행
                for i in range(self.CPU.n_core - len(self.queue)):
                    self.CPU.exec_idle(time=1)
            else:
                for i in range(self.CPU.n_core):
                    exec_task_list.append(self.pop_queue())

            # for active tasks (1 unit 실행)
            for exec_task in exec_task_list:
                exec_task.exec_active(system=self, time=1)

            # for other idle tasks (전력 소모 계산 및 1초 흐르기)
            for i in range(len(self.queue)):
                task = self.queue[i][1]
                task.exec_idle(time=1, update_deadline=True)
                self.queue[i] = (task.calc_priority(), task)
            heapq.heapify(self.queue)  # 재정렬 필요
            for tup in self.wait_period_queue:
                tup[1].exec_idle(time=1, update_deadline=False)

            self.add_utilization()

            # 실행된 task의 주기 끝났는지 확인해서 끝났으면 초기화 시키고 wait으로
            for exec_task in exec_task_list:
                if exec_task.det_remain == 0:
                    exec_task.period_start += exec_task.period
                    exec_task.det_remain = exec_task.det
                    exec_task.deadline = exec_task.period
                    self.push_wait_period_queue(exec_task)
                else:
                    self.push_queue(exec_task)

            self.check_queued_tasks()
            self.time += 1
            self.check_wait_period_queue()

        report = Report(self)
        report.print_console()
        return report

    def push_wait_period_queue(self, task):
        heapq.heappush(self.wait_period_queue, (task.period_start, task))

    def push_queue(self, task):
        heapq.heappush(self.queue, (task.calc_priority(), task))

    def pop_wait_period_queue(self):
        return heapq.heappop(self.wait_period_queue)[1]

    def pop_queue(self):
        return heapq.heappop(self.queue)[1]

    def check_wait_period_queue(self):
        # wait_queue 에 있는 task 중 새 주기가 시작되는 태스크를 queue로 이동.
        while len(self.wait_period_queue) != 0:
            if self.wait_period_queue[0][0] > self.time:
                break
            task = heapq.heappop(self.wait_period_queue)[1]
            self.push_queue(task)

    def add_utilization(self):
        self.sum_utils += self.get_tasks_ndet()
        self.n_utils += 1

    @abstractmethod
    def assign_task(self, task) -> bool:
        pass

    @abstractmethod
    def reassign_task(self, task) -> bool:
        pass

    def get_tasks_ndet(self) -> float:
        result = 0.0
        for task in self.tasks:
            result += float(task.det) / task.period
        return result

    def get_tasks_ndet_except(self, task_except) -> float:
        result = 0.0
        for task in self.tasks:
            if task.no != task_except.no:
                result += task.det / task.period
        return result

    def is_schedule(self, task) -> bool:
        if self.get_tasks_ndet_except(task) + (task.det / task.period) <= self.CPU.n_core:
            return True
        return False

    def setup_tasks(self) -> bool:
        for task in self.tasks:
            if not self.assign_task(task):
                raise Exception(task.no + ": insufficient memory")
            task.calc_det()
            if not self.is_schedule(task):
                raise Exception(task.no + ": unschedule task")
            self.push_queue(task)
        return True

    def check_queued_tasks(self):
        for task in self.tasks:
            task.check_task()

    @staticmethod
    def error(self, message: str):
        print(message)
        sys.exit()

    def print_queue(self):
        temp = []
        print("-----------queue------------")
        while len(self.queue) > 0:
            tup = heapq.heappop(self.queue)
            print(tup[1].desc_task())
            temp.append(tup)
        print("---------queue end-----------")
        heapq.heapify(temp)
        self.queue = temp


class Dram(System):
    def __init__(self, end_sim_time: int, verbose: int):
        super().__init__(end_sim_time, verbose)
        self.name = "DRAM"
        self.desc = "No DVFS with dram(dram)"
        self.CPU = NoneDVFSCPU()

    def assign_task(self, task) -> bool:
        self.CPU.assign_cpu_frequency(task)
        return self.memories.assign_memory(task, Memory.TYPE_DRAM)

    def reassign_task(self, task) -> bool:
        return self.CPU.reassign_cpu_frequency(task, self)


class Hm(System):
    def __init__(self, end_sim_time: int, verbose: int):
        super().__init__(end_sim_time, verbose)
        self.name = "HM"
        self.desc = "Hybrid memory(hm)"
        self.CPU = NoneDVFSCPU()

    def assign_task(self, task) -> bool:
        self.CPU.assign_cpu_frequency(task)

        mem_types = [Memory.TYPE_DRAM, Memory.TYPE_LPM]
        for mem_type in mem_types:
            if self.memories.assign_memory(task, mem_type):
                return True
        return False

    def reassign_task(self, task) -> bool:
        self.CPU.reassign_cpu_frequency(task, self)

        task.revoke_memory()

        mem_types = [Memory.TYPE_LPM, Memory.TYPE_DRAM]
        for mem_type in mem_types:
            if self.memories.assign_memory(task, mem_type):
                task.calc_det()
                if self.is_schedule(task):
                    return True
                task.revert_det()
        return False


class DvfsDram(System):
    def __init__(self, end_sim_time: int, verbose: int):
        super().__init__(end_sim_time, verbose)
        self.name = "DVFS_DRAM"
        self.desc = "DVFS with dram(dvfs-dram)"
        self.CPU = DVFSCPU()

    def assign_task(self, task) -> bool:
        self.CPU.assign_cpu_frequency(task)
        if not self.memories.assign_memory(task, Memory.TYPE_DRAM):
            return False
        return True

    def reassign_task(self, task) -> bool:
        return self.CPU.reassign_cpu_frequency(task, self)


class DvfsHm(System):
    def __init__(self, end_sim_time: int, verbose: int):
        super().__init__(end_sim_time, verbose)
        self.name = "DVFS_HM"
        self.desc = "DVFS with hybrid memory(dvs-hm)"
        self.CPU = DVFSCPU()

    def assign_task(self, task) -> bool:
        self.CPU.assign_cpu_frequency(task)

        mem_types = [Memory.TYPE_DRAM, Memory.TYPE_LPM]
        for mem_type in mem_types:
            if self.memories.assign_memory(task, mem_type):
                return True
        return False

    def reassign_task(self, task) -> bool:
        task.revoke_memory()

        mem_types = [Memory.TYPE_LPM, Memory.TYPE_DRAM]
        for mem_type in mem_types:
            if self.memories.assign_memory(task, mem_type):
                if self.CPU.reassign_cpu_frequency(task, self):
                    return True
                task.revoke_memory()
        return False


class GA(System):
    def __init__(self, end_sim_time: int, verbose: int):
        super().__init__(end_sim_time, verbose)
        self.name = "GA(Fixed)"
        self.desc = "Mode for GA"
        self.CPU = DVFSCPU()
        self.assigned_CPU = []
        self.assigned_MEM = []

    def run(self):
        # Set input files
        InputUtils.set_processor(self)
        InputUtils.set_memory(self)
        InputUtils.set_tasks(self)
        InputUtils.set_GA(self)
        self.setup_tasks()

        # Run simulator...
        while self.time < self.end_sim_time:
            if self.verbose == System.V_DETAIL:
                print(f'\ntime = {self.time}')
                self.print_queue()

            # time 부터 (time+1)동안 실행될 task 코어의 개수만큼 고르기.
            exec_task_list = []
            if len(self.queue) < self.CPU.n_core:
                # 큐에 있는 것 모두 실행가능(코어의 개수보다 적으므로)
                for tup in self.queue:
                    exec_task_list.append(tup[1])
                self.queue = []

                # self.CPU.n_core - len(self.queue)개의 코어는 idle로 실행
                for i in range(self.CPU.n_core - len(self.queue)):
                    self.CPU.exec_idle(time=1)
            else:
                for i in range(self.CPU.n_core):
                    exec_task_list.append(self.pop_queue())

            # for active tasks (1 unit 실행)
            for exec_task in exec_task_list:
                exec_task.exec_active(system=self, time=1)

            # for other idle tasks (전력 소모 계산 및 1초 흐르기)
            for i in range(len(self.queue)):
                task = self.queue[i][1]
                task.exec_idle(time=1, update_deadline=True)
                self.queue[i] = (task.calc_priority(), task)
            heapq.heapify(self.queue)  # 재정렬 필요
            for tup in self.wait_period_queue:
                tup[1].exec_idle(time=1, update_deadline=False)

            self.add_utilization()

            # 실행된 task의 주기 끝났는지 확인해서 끝났으면 초기화 시키고 wait으로
            for exec_task in exec_task_list:
                if exec_task.det_remain == 0:
                    exec_task.period_start += exec_task.period
                    exec_task.det_remain = exec_task.det
                    exec_task.deadline = exec_task.period
                    self.push_wait_period_queue(exec_task)
                else:
                    self.push_queue(exec_task)

            self.check_queued_tasks()
            self.time += 1
            self.check_wait_period_queue()

        report = Report(self)
        report.print_console()
        return report

    def setup_tasks(self) -> bool:
        for i in range(len(self.tasks)):
            task = self.tasks[i]

            # Set cpu
            task.cpu_frequency = self.CPU.frequencies[self.assigned_CPU[i]]

            # Set memory
            memory = self.memories.list[self.assigned_MEM[i]]
            task.memory = memory
            memory.used_capacity += task.memory_req

            task.calc_det()
            if not self.is_schedule(task):
                raise Exception(task.no + ": unschedule task")
            self.push_queue(task)

        # Check memory
        if not self.memories.check_memory():
            raise Exception(task.no + ": need more memory")
        return True

    def assign_task(self, task) -> bool:
        pass

    def reassign_task(self, task) -> bool:
        pass
