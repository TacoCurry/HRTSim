from System import SystemOriginal, SystemGA
from Input import *


# Original
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()

SystemOriginal(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()

# GA
sim_time, verbose, processor, memories = get_configuration()
rt_tasks = get_rt_tasks()
non_rt_tasks = get_non_rt_tasks()

SystemGA(sim_time, verbose, processor, memories, rt_tasks, non_rt_tasks).run()



