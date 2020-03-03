from System import System


class SystemOriginal(System):
    # 경성 태스크를 항상 오리지널 방식으로 수행하며, 비실시간이 들어오면 남는시간에 실행시켜주는 방식
    # 대조군. 유전알고리즘 쓰지 않음.

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

            exec_tasks = []

            if len(self.rt_queue) < self.processor.n_core:
                # 큐에 있는 것 모두 실행가능(코어의 개수보다 적으므로)
                for tup in self.rt_queue:
                    exec_tasks.append(tup[1])
                self.rt_queue = []

                if len(self.non_rt_queue) == 0:
                # 비 실시간 없는 경우: self.processor.n_core - len(self.queue)개의 코어는 idle로 실행
                    for i in range(self.processor.n_core - len(self.rt_queue)):
                        self.CPU.exec_idle(time=1)
                else:
                    # 비실시간 있는 경우
                    for i in range(self.processor.n_core - len(self.rt_queue)):
                       # 비실시간 오리지널로 수행
                    pass

            else:
                for i in range(self.CPU.n_core):
                    exec_tasks.append(self.pop_queue())

            # for active rt tasks (1 quantum 실행)
            for exec_task in exec_tasks:
                exec_task.mode = 'O'
                exec_task.exec_active()


            # TODO 실행된 rt-task의 주기 끝났는지 확인해서 끝났으면 초기화 시키고 wait으로

            # TODO non-rt-task의 실행이 끝났다면( bt == exec time)  end_time 등을 기록하기

            cur_time += 1
            self.check_rt_tasks(cur_time)

        self.print_final_report()
