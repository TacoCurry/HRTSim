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

        self.non_rt_queue = []
        self.non_rt_tasks_point = 0

    def print_debug(self, time):
        # TODO rt_queue와 non_rt_queue 출력 코드 필요
        if self.verbose == System.VERBOSE_DEBUG_HARD:
            pass

    def setup_tasks(self):
        # TODO 시뮬레이션 시작 전 태스크 셋팅하는 코드
        # 모든 rt_task들을 rt_wait_queue에 넣어야 할듯.. 0 퀀텀에서 모두 주기 시작이므
        pass

    def check_new_non_rt(self, time):
        # TODO 새로 들어온 non_rt 태스크가 존재하는지 확인 후로, 있다 non_rt_queue에 넣어주는 코드면
        # 동시에 여러 태스크가 들어올 수 있다는 점에도 유의
        pass

    def check_wait_peroid_queue(self, time):
        # TODO rt_wait_queue에서 다음 주기의 시작을 기다리고 있는 rt_task 확인하고 새로운 주기이면 큐 옮겨주기
        pass

    def print_final_report(self):
        # TODO 최종 결과 출력하는 코드
        pass

    def push_rt_queue(self, rt_task):
        # TODO rt_queue에 넣어주는 코드.
        # PD2를 이용하여 우선순위를 게산한 후 다음과 같은 형태로 넣어주어야함
        # heapq.heappush(self.rt_queue, (priority, rt_task))
        pass

    def push_rt_wait_queue(self, rt_task):
        heapq.heappush(self.rt_wait_queue, (rt_task.next_period_start, rt_task))

    def check_rt_tasks(self, time):
        # TODO 데드라인 넘는 태스트는 없는지 확인?
        # priority에 대해 정렬해야 한다면 정렬 해...
        pass


class SystemOriginal(System):
    # 경성 태스크를 항상 오리지널 방식으로 수행하며, 비실시간이 들어오면 남는시간에 실행시켜주는 방식
    # 대조군. 유전알고리즘 쓰지 않음.

    def __init__(self, sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks):
        super().__init__(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks)

    def run(self):
        self.setup_tasks()

        cur_time = 0
        while cur_time < self.sim_time:
            self.print_debug(cur_time)
            self.check_new_non_rt(cur_time)
            self.check_wait_period_queue(cur_time)

            exec_tasks = []
            if len(self.rt_queue) < self.processor.n_core:
                # non_rt_task를 실행할 수 있는 idle 존재
                pass
            else:
                # idle 존재 X
                pass

            # TODO 실행된 task의 주기 끝났는지 확인해서 끝났으면 초기화 시키고 wait으로
            # TODO non-rt-task의 실행이 끝났다면 기록하기

            cur_time += 1
            self.check_rt_tasks(cur_time)

        self.print_final_report()


class SystemGA(System):
    # 대기중인 non-rt-task가 존재하면 Original과 같은 방식으로 실행.
    # 존재하지 않는다면 유전 알고리즘 결과를 이용하여 실행.

    def __init__(self, sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks):
        super().__init__(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks)

    def run(self):
        self.setup_tasks()

        cur_time = 0
        while cur_time < self.sim_time:
            self.print_debug(cur_time)
            self.check_new_non_rt(cur_time)
            self.check_wait_period_queue(cur_time)

            if len(self.non_rt_queue) == 0:
                # 수행 대기중인 non-rt-tasks가 없다면 유전알고리즘으로 수행
                pass
            else:
                # 수행 대기중인 non-rt-tasks가 잇다면 original로..?
                pass

            # TODO 실행된 task의 주기 끝났는지 확인해서 끝났으면 초기화 시키고 wait으로
            # TODO non-rt-task의 실행이 끝났다면 기록하기

            cur_time += 1
            self.check_rt_tasks(cur_time)

        self.print_final_report()
