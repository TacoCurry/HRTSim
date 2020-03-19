from SystemOriginal import SystemOriginal
from SystemGA import SystemGA
from SystemIGA import SystemIGA
from SystemADH import SystemADH
from SystemPS import SystemPS
from SystemPM import SystemPM
from Input import *
from Task import RTTask, NonRTTask

# Original
RTTask.total_power = NonRTTask.total_power = 0
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()
set_ga_results(rt_tasks)

SystemOriginal(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()


# GA (지연방식)
RTTask.total_power = NonRTTask.total_power = 0
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()
set_ga_results(rt_tasks)

SystemGA(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()


# IGA(즉시 변경 방식)
RTTask.total_power = NonRTTask.total_power = 0
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()
set_ga_results(rt_tasks)

SystemIGA(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

# ADH(비실시간 DVFS, HM)
RTTask.total_power = NonRTTask.total_power = 0
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()
set_ga_results(rt_tasks)

SystemADH(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

# PS(비실시간 담당 코어가 1)
RTTask.total_power = NonRTTask.total_power = 0
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()
set_ga_results(rt_tasks)

SystemPS(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

# PM(비실시간 담당 코어가 다수일 수 있음)
RTTask.total_power = NonRTTask.total_power = 0
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()
max_core, min_core = set_ga_results(rt_tasks)

SystemPM(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks, max_core, min_core).run()


