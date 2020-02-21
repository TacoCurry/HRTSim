from Memory import Memories
from Task import Task


class InputUtils:
    @staticmethod
    def set_processor(system, input_file="input_processor.txt"):
        try:
            with open(input_file, "r", encoding='UTF8') as f:
                system.CPU.n_core = int(f.readline())
                n_frequency = int(f.readline())
                for i in range(n_frequency):
                    temp = f.readline().split()
                    system.CPU.insert_cpu_frequency(
                        wcet_scale=float(temp[0]), power_active=float(temp[1]), power_idle=float(temp[2]))
        except FileNotFoundError:
            system.error("processor 설정 파일을 찾을 수 없습니다.")

    @staticmethod
    def set_memory(system, input_file="input_mem.txt"):
        try:
            system.memories = Memories()
            with open(input_file, "r", encoding='UTF8') as f:
                for i in range(2):
                    temp = f.readline().split()
                    system.memories.insert_memory(memory_str=temp[0], capacity=int(temp[1]), wcet_scale=float(temp[2]),
                                                  power_active=float(temp[3]), power_idle=float(temp[4]))
        except FileNotFoundError:
            system.error("memory 정보 파일을 찾을 수 없습니다.")

    @staticmethod
    def set_tasks(system, input_file="input_tasks.txt"):
        # 일단 tasks 에 순서대로 담기
        try:
            with open(input_file, "r", encoding='UTF8') as f:
                n_task = int(f.readline())
                for i in range(n_task):
                    temp = f.readline().split()
                    system.tasks.append(Task(no=i+1, wcet=int(temp[0]), period=int(temp[1]),
                                             mem_req=int(temp[2]), mem_active_ratio=float(temp[3]), cpu=system.CPU))
        except FileNotFoundError:
            system.error("task 정보 파일을 찾을 수 없습니다.")

    @staticmethod
    def set_GA(system, input_file="GA_result.txt"):
        try:
            with open(input_file, "r", encoding='UTF8') as f:
                n_task = len(system.tasks)
                for i in range(n_task):
                    temp = f.readline().split()
                    system.assigned_CPU.append(int(temp[0]))
                    system.assigned_MEM.append(int(temp[1]))
        except FileNotFoundError:
            system.error("GA 정보 파일을 찾을 수 없습니다.")