# 경성 태스크를 항상 오리지널 방식으로 수행하며, 비실시간이 들어오면 남는시간에 실행시켜주는 방식
# 대조군 알고리즘. 유전알고리즘 쓰지 않음.
from abc import *
from Processor import NoneDVFSCPU, DVFSCPU
from Memory import Memory
import heapq
import sys
from Input import InputUtils
from Report import Report
from System import System,Dram

class Original(System):
    def __init__(self, end_sim_time: int, verbose: int):
        super().__init__(end_sim_time, verbose)
        self.name = "RT+nRT_original"
        self.desc = "Mode for RT+nRT_original"
        self.CPU = NoneDVFSCPU()
        self.assigned_CPU = []
        self.assigned_MEM = []

    def run(self):
        # Set input files
        InputUtils.set_processor(self)
        InputUtils.set_memory(self)
        InputUtils.set_tasks(self)
        InputUtils.set_noneRTtasks(self)
        self.setup_tasks()

        ''''# Run simulator...
        while self.time < self.end_sim_time:
            if(len(self.non_rt_tasks)) == 0:
             DRAM 수행'''

        '''else: 코어의 개수 - 유틸의 합 만큼 비실시간 수행'''



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

            # Set cpu - 1 번째
            task.cpu_frequency = self.CPU.frequencies[0]

            # Set memory - 1 번째
            memory = self.memories.list[0]
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
