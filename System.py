from abc import *
import heapq


class System(metaclass=ABCMeta):
    VERBOSE_SIMPLE = 0
    VERBOSE_DEBUG = 1
    VERBOSE_DEBUG_HARD = 2

    def __init__(self, sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks):
        self.sim_time = sim_time

        self.verbose = verbose
        self.processor = processor
        self.memories = memories

        self.rt_tasks = rt_tasks
        self.non_rt_tasks = non_rt_tasks

        # 현재 주기안에서 실행 대기중인 rt-task가 담김
        # 원소는 (PD2를 이용한 우선순위, 태스크 인스턴스)로 담아서 우선순위 큐로 구현
        self.rt_queue = []

        # 현재 주기 수행은 끝났으며 다음 주기의 시작을 기다리는 rt-task가 담김
        # 원소는 (다음 주기 시작시간, 태스크 인스턴스)로 담아서 주기 시작시간에 대한 우선순위 큐로 구현
        self.rt_wait_queue = []

        # 그냥 리스트 (우선순위 큐 아님)
        self.non_rt_queue = []

        # 시작시간(at) 오름차순 -> 매 시간마다 확인 필요. 맨앞의 태스크만 확인하면 된다.
        self.non_rt_tasks_pointer = 0

    def print_debug(self, time):
        # 디버그를 위해 rt_queue와 non_rt_queue 출력
        print("current time: {}".format(time))

        temp_queue = []
        print("==========rt_queue===========")
        while len(self.rt_queue) > 0:
            rt_task = heapq.heappop(self.rt_queue)
            print(rt_task.desc_task())
            temp_queue.append(rt_task)
        print("===========the end===========")
        heapq.heapify(temp_queue)
        self.rt_queue = temp_queue

        print("==========non_rt_queue===========")
        for non_rt_task in self.non_rt_tasks:
            non_rt_task.desc_task()
        print("===========the end===========")

    def check_new_non_rt(self, cur_time):
        if self.non_rt_tasks_pointer < len(self.non_rt_tasks) and self.non_rt_tasks[self.non_rt_tasks_pointer] == cur_time:
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

    def print_final_report(self):
        # TODO 최종 결과 출력하는 코드
        pass

    def push_rt_queue(self, rt_task):
        heapq.heappush(self.rt_queue, rt_task)

    def push_rt_wait_queue(self, rt_task):
        heapq.heappush(self.rt_wait_queue, (rt_task.next_period_start, rt_task))

    def check_rt_tasks(self, cur_time):
        # 데드라인 넘는 태스트는 없는지 확인? 있으면 에러
        for rt_task in self.rt_tasks:
            rt_task.is_deadline_violated(cur_time)

    def setup_tasks(self):
        # 시뮬레이션 시작 전 태스크 셋팅하는 코드
        for rt_task in self.rt_tasks:
            self.push_rt_wait_queue(rt_task)

    def get_tasks_ndet(self) -> float:
        result = 0.0
        for rt_task in self.rt_tasks:
            result += float(rt_task.det) / rt_task.period
        return result

    def add_utilization(self):
        self.sum_utils += self.get_tasks_ndet()
        self.n_utils += 1