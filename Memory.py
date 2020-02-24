class Memory:
    TYPE_NONE = 0
    TYPE_DRAM = 1
    TYPE_LPM = 2

    def __init__(self, capacity, wcet_scale, power_active, power_idle):
        self.type = None
        self.capacity = capacity
        self.wcet_scale = wcet_scale
        self.power_active = power_active
        self.power_idle = power_idle
        self.used_capacity = 0

        self.power_consumed_idle = 0
        self.power_consumed_active = 0

    def get_type_str(self):
        if self.type == Memory.TYPE_DRAM:
            return "DRAM"
        elif self.type == Memory.LPM:
            return "LPM"
        else:
            return "None"

    def add_power_consumed_idle(self, power: float):
        self.power_consumed_idle += power

    def add_power_consumed_active(self, power: float):
        self.power_consumed_active += power


class LPM(Memory):
    def __init__(self, capacity, wcet_scale, power_active, power_idle):
        super().__init__(capacity, wcet_scale, power_active, power_idle)
        self.type = Memory.TYPE_LPM


class DRAM(Memory):
    def __init__(self, capacity, wcet_scale, power_active, power_idle):
        super().__init__(capacity, wcet_scale, power_active, power_idle)
        self.type = Memory.TYPE_DRAM


class Memories:
    def __init__(self):
        self.list = []
        self.n_mem_types = 0
        self.total_capacity = 0

        self.total_power_consumed_active = None
        self.total_power_consumed_idle = None

    def get_memory(self, memory_type):
        for memory in self.list:
            if memory.type == memory_type:
                return memory
        return None

    def insert_memory(self, memory_str, capacity, wcet_scale, power_active, power_idle):
        if memory_str.lower() == "lpm":
            self.list.append(LPM(capacity, wcet_scale, power_active, power_idle))
        elif memory_str.lower() == "dram":
            self.list.append(DRAM(capacity, wcet_scale, power_active, power_idle))
        else:
            return False

        self.n_mem_types += 1
        self.total_capacity += capacity
        return True

    def init_memories(self):
        self.total_capacity = 0
        for memory in self.list:
            memory.used_capacity = 0
            self.total_capacity += memory.capacity

    def calc_total_power_consumed(self):
        self.total_power_consumed_active = sum([memory.power_consumed_active for memory in self.list])
        self.total_power_consumed_idle = sum([memory.power_consumed_idle for memory in self.list])

    def check_memory(self):
        # Check memory usage
        for memory in self.list:
            if memory.used_capacity > memory.capacity:
                return False
        return True