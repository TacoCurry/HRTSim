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

        # 시작시간 오름차순 -> 매 시간마다 확인 필요. 맨앞의 태스크만 확인하면 된다.
        self.non_rt_tasks_point = 0

    def print_debug(self, time):
        #  rt_queue와 non_rt_queue 출력 코드 필요
        temp1 = []
        print("==========rt_queue===========")
        while len(self.rt_queue) > 0 :
            tup = heapq.heappop(self.rt_queue)
            print(tup[1].desc_task())
            temp1.append(tup)
        print("===========the end===========")
        heapq.heapify(temp1)
        self.rt_queue = temp1

        temp2 = []
        print("==========rt_queue===========")
        while len(self.non_rt_queue) > 0 :
            tup = heapq.heappop(self.non_rt_queue)
            print(tup[1].desc_task())
            temp2.append(tup)
        print("===========the end===========")
        heapq.heapify(temp2)
        self.non_rt_queue = temp2




    def check_new_non_rt(self, time):
        # TODO 새로 들어온 non_rt 태스크가 존재하는지 확인 후로, 있다 non_rt_queue에 넣어주는 코드면
        # 동시에 여러 태스크가 들어올 수 있다는 점에도 유의, 포인터 사용 해야함.
        pass

    def check_wait_peroid_queue(self, time):
        # rt_wait_queue에서 다음 주기의 시작을 기다리고 있는 rt_task 확인하고 새로운 주기이면 큐 옮겨주기
        while len(self.rt_wait_queue) != 0:
            if self.self.rt_wait_queue[0][0] > self.time:
                break
            rt_task = heapq.heappop(self.rt_wait_queue)[1]
            self.push_rt_queue(rt_task)



    def print_final_report(self):
        # TODO 최종 결과 출력하는 코드
        pass

    def push_rt_queue(self, rt_task):
        heapq.heappush(self.rt_queue, rt_task)

    def push_rt_wait_queue(self, rt_task):
        heapq.heappush(self.rt_wait_queue, (rt_task.next_period_start, rt_task))

    def check_rt_tasks(self, time):
        # 데드라인 넘는 태스트는 없는지 확인? 있으면 에러
        for rt_task in self.rt_tasks:
            rt_task.is_deadline_violated()

    def setup_tasks(self):
        # 시뮬레이션 시작 전 태스크 셋팅하는 코드
        # 모든 rt_task들을 rt_wait_queue에 넣어야 할듯.. 0 퀀텀에서 모두 주기 시작이므
        for rt_task in self.rt_tasks:
            self.push_rt_wait_queue(rt_task)


