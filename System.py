from abc import *
import heapq
from collections import deque
from Task import RTTask, NonRTTask


class System(metaclass=ABCMeta):
    VERBOSE_SIMPLE = 0
    VERBOSE_DEBUG = 1
    VERBOSE_DEBUG_HARD = 2

    def __init__(self, sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks):
        self.name = None
        self.sim_time = sim_time

        self.verbose = verbose
        self.processor = processor
        self.memories = memories

        self.rt_tasks = rt_tasks
        self.non_rt_tasks = non_rt_tasks
        self.non_rt_tasks_pointer = 0  # 시작시간(at) 오름차순이기 때문에 pointer가 가리키는 태스크만 매 시간 확인하면 된다.

        # 현재 주기안에서 실행 대기중인 rt-task가 담김
        # 원소는 (PD2를 이용한 우선순위, 태스크 인스턴스)로 담아서 우선순위 큐로 구현
        self.rt_queue = []

        # 현재 주기 수행은 끝났으며 다음 주기의 시작을 기다리는 rt-task가 담김
        # 원소는 (다음 주기 시작시간, 태스크 인스턴스)로 담아서 주기 시작시간에 대한 우선순위 큐로 구현
        self.rt_wait_queue = []

        # 실행 대기중인 non-rt-task가 담김
        self.non_rt_queue = deque()

        # 시뮬레이션 결과를 위해 유지
        self.sum_utils = 0

    def print_debug(self, time):
        temp_queue = []
        if len(self.rt_queue) > 0:
            print("==========rt_queue===========")
            while len(self.rt_queue) > 0:
                rt_task = heapq.heappop(self.rt_queue)
                print(rt_task.desc_task())
                temp_queue.append(rt_task)
            print("========rt_queue_end=========")
            heapq.heapify(temp_queue)
            self.rt_queue = temp_queue

        if len(self.non_rt_queue) > 0:
            print("==========non_rt_queue===========")
            for non_rt_task in self.non_rt_queue:
                print(non_rt_task.desc_task())
            print("=======  non_rt_queue end==========")

    def check_new_non_rt(self, cur_time):
        if self.non_rt_tasks_pointer < len(self.non_rt_tasks) and \
                self.non_rt_tasks[self.non_rt_tasks_pointer].at == cur_time:
            self.non_rt_queue.append(self.non_rt_tasks[self.non_rt_tasks_pointer])
            self.non_rt_tasks_pointer += 1

    def check_wait_period_queue(self, cur_time):
        # rt_wait_queue에서 다음 주기의 시작을 기다리고 있는 rt_task 확인하고 새로운 주기가 시작된다면 큐 옮겨주기
        new_start_rt_tasks = []
        while len(self.rt_wait_queue) > 0:
            if self.rt_wait_queue[0][0] > cur_time:
                break
            rt_task = heapq.heappop(self.rt_wait_queue)[1]
            new_start_rt_tasks.append(rt_task)
        return new_start_rt_tasks

    def push_rt_queue(self, rt_task):
        heapq.heappush(self.rt_queue, rt_task)

    def push_rt_wait_queue(self, rt_task):
        heapq.heappush(self.rt_wait_queue, (rt_task.next_period_start, rt_task))

    def check_rt_tasks(self, cur_time):
        for rt_task in self.rt_tasks:
            rt_task.is_deadline_violated(cur_time)

    def add_cpu_utilization(self, util):
        self.sum_utils += util

    def calc_original_util(self):
        return sum([task.wcet/task.period for task in self.rt_tasks])

    def print_final_report(self):
        print("===============final report===============")
        self.print_core_num()
        self.print_policy_name()
        self.print_task_num()
        self.print_simulation_time()
        self.print_power()
        self.print_wait_time()
        self.print_util()
        print("===========================================")

    def print_core_num(self):
        print(f'Number of core: {self.processor.n_core}')

    def print_task_num(self):
        print(f'Number of RT task: {len(self.rt_tasks)}')
        print(f'Number of non RT task: {len(self.non_rt_tasks)}')
        print(f'Number of total task: {len(self.rt_tasks)} + {len(self.non_rt_tasks)}')

    def print_policy_name(self):
        print(f'Name of policy: {self.name}')

    def print_simulation_time(self):
        print(f'Simulation_time: {self.sim_time}')

    def print_power(self):
        self.memories.calc_total_power_consumed()

        power_processor = self.processor.power_consumed_idle + self.processor.power_consumed_active
        power_memory = self.memories.total_power_consumed_idle + self.memories.total_power_consumed_active
        power_active = self.processor.power_consumed_active + self.memories.total_power_consumed_active
        power_idle = self.processor.power_consumed_idle + self.memories.total_power_consumed_idle
        power = power_processor + power_memory

        print(f'Average power consumed: {round(power / self.sim_time, 3)}')
        print(f'PROCESSOR + MEM power consumed: {round(power_processor / self.sim_time, 3)} + '
              f'{round(power_memory / self.sim_time, 3)}')
        print(f'ACTIVE + IDLE power consumed: '
              f'{round(power_active / self.sim_time, 3)} + {round(power_idle / self.sim_time, 3)}')
        print('RT-TASK + NONE-RT-TASK power consumed: {} + {}'.format(round(RTTask.total_power / self.sim_time, 3),
                                                                      round(NonRTTask.total_power / self.sim_time, 3)))

    def print_util(self):
        avg_cpu_util = self.sum_utils / self.sim_time
        print('utilization: {}%'.format(avg_cpu_util))

    def print_wait_time(self):
        total_wait_time = total_response_time = total_turnaround_time = count = 0

        for non_rt_task in self.non_rt_tasks:
            if non_rt_task.end_time:
                count += 1
                wait_time = (non_rt_task.end_time - non_rt_task.at) - non_rt_task.bt
                total_wait_time += wait_time
                response_time = non_rt_task.start_time - non_rt_task.at
                total_response_time += response_time
                turnaround_time = non_rt_task.end_time - non_rt_task.at
                total_turnaround_time += turnaround_time

        print(f'Average wait time: {format(total_wait_time / count, ".4f")}')
        print(f'Average response time: {format(total_response_time / count, ".4f")}')
        print(f'Average turnaround time: {format(total_turnaround_time / count, ".4f")}')
