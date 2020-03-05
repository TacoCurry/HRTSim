from System import System


class SystemIGA(System):
    # 대기중인 non-rt-task가 존재하면 Original과 같은 방식으로 실행.
    # 존재하지 않는다면 유전 알고리즘 결과를 이용하여 실행.

    def __init__(self, sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks):
        super().__init__(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks)

    def run(self):
        self.setup_tasks()

        cur_time = 0
        while cur_time < self.sim_time:
            if self.verbose == System.VERBOSE_DEBUG_HARD:
                self.print_debug(cur_time)

            self.check_new_non_rt(cur_time)  # 새롭게 들어온 non_rt_job인 이 있는지 확인
            self.check_wait_period_queue(cur_time)  # 새롭게 주기 시작하는 job이 있는지 확인

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
