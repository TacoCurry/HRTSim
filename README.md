# RTSim
Real-time task simulator

## Policy
- Original(Non-DVFS with DRAM)
- HM(Non-DVFS with DRAM and LPM)
- DVFS-DRAM(DVFS with DRAM)
- DVFS-HM(DVFS with DRAM and LPM)
- Fixed(태스크 최적화의 결과를 입력으로 받는 모드)

## Input
자세한 내용은 파일 내부의 설명을 참고하세요.
- input_mem.txt: 메모리의 종류, 종류 별 실행률, 용량, active 상태의 전력소모량, idle 상태의 전력소모량 
- input_processer.txt: 프로세서의 코어 개수, voltage/frequency 모드의 개수, 모드 별 실행률, active 상태의 전력소모량, idle 상태의 전력소모량
- input_tasks.txt: 태스크의 개수, 태스크 별 최악수행시간, 주기, 메모리 요구량
- GA_result.txt: 태스크 최적화의 결과로, 각 task가 실행될 voltage/frequency 모드와 메모리의 종류.

## Run
시뮬레이션 하고자 하는 정보를 위 input 파일에 형식을 맞추어 입력하고, Main.py를 실행한다.<br>
시뮬레이션 하고자 하는 시간과 policy를 콘솔 입력한다.

## Output
총 전력소모량, 프로세서 Utilization, CPU 전력소모량, 메모리 전력소모량, active 시 전력소모량, idle시 전력소모량 등이 콘솔로 출력된다.

## Demo
RT Simulator Demo: DVFS_HM Policy 수행 결과 
https://youtu.be/SBjRZtSTYgk

