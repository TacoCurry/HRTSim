from Memory import Memories
from Task import RTTask, NonRTTask
import sys
from Processor import Processor


def get_processor_and_memory(input_file="input_configuration.txt"):
    try:
        processor = None
        memories = None

        with open(input_file, "r", encoding='UTF-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break  # EOF

                line = line.split()
                if line[0] == '##':
                    if line[1] == 'Memory':
                        memories = get_memory(f)
                    elif line[1] == 'Processor':
                        processor = get_processor(f)

        assert processor, memories
        return processor, memories

    except FileNotFoundError:
        print("Cannot find {}".format(input_file))
        sys.exit(0)


def get_processor(f):
    processor = Processor(int(f.readline()))
    while True:
        line = f.readline().split()
        if len(line) == 0:
            break
        processor.insert_processor_mode(*map(float, line))
    return processor


def get_memory(f):
    memories = Memories()
    while True:
        line = f.readline().split()
        if len(line) == 0:
            break
        memories.insert_memory(str(line[0]), int(line[1]), *map(float, line[2:]))
    return memories


def get_rt_tasks(input_file="input_rt_tasks.txt"):
    try:
        rt_tasks = []
        with open(input_file, "r", encoding='UTF-8') as f:
            for i in range(int(f.readline())):
                line = f.readline().split()
                rt_tasks.append(RTTask(i+1, *map(int, line[:3]), float(line[3])))

        return rt_tasks

    except FileNotFoundError:
        print("Cannot find {}".format(input_file))
        sys.exit(0)


def get_non_rt_tasks(input_file="input_nonrt_tasks.txt"):
    try:
        non_rt_tasks = []
        with open(input_file, "r", encoding='UTF-8') as f:
            for i in range(int(f.readline())):
                line = f.readline().split()
                # TODO NoneRTTTask의 memory 관련 정보도 받도록 수정해야해요.
                non_rt_tasks.append(NonRTTask(i + 1, *map(int, line)))

        return non_rt_tasks

    except FileNotFoundError:
        print("Cannot find {}".format(input_file))
        sys.exit(0)


def set_ga_results(rt_tasks, input_file="input_ga_results.txt"):
    try:
        with open(input_file, "r", encoding='UTF8') as f:
            for task in rt_tasks:
                line = map(int, f.readline().split())
                task.ga_processor_mode = line[0]
                task.ga_memory_mode = line[1]

    except FileNotFoundError:
        print("Cannot find {}".format(input_file))
        sys.exit(0)
