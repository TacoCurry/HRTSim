from SystemOriginal import SystemOriginal
from SystemGA import SystemGA
from SystemIGA import SystemIGA
from Input import *


# Original
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()

SystemOriginal(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

# GA (지연방식)
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()

SystemGA(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

# IGA(즉시 변경 방식)
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()

SystemIGA(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

