from System import Dram, Hm, DvfsDram, DvfsHm, GA

system = int(input("[1]DRAM, [2]HM, [3]DVFS_DRAM, [4]DVFS_HM, [5]FIXED(GA), [6]ALL: "))
end_sim_time = int(input("시뮬레이션 시간: "))
verbose = int(input("상세 출력(0:없음, 1:실행결과만, 2:자세히): "))

if system == 1:
    Dram(end_sim_time, verbose).run()
elif system == 2:
    Hm(end_sim_time, verbose).run()
elif system == 3:
    DvfsDram(end_sim_time, verbose).run()
elif system == 4:
    DvfsHm(end_sim_time, verbose).run()
elif system == 5:
    GA(end_sim_time, verbose).run()
elif system == 6:
    Dram(end_sim_time, verbose).run()
    Hm(end_sim_time, verbose).run()
    DvfsDram(end_sim_time, verbose).run()
    DvfsHm(end_sim_time, verbose).run()
    GA(end_sim_time, verbose).run()



