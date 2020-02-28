## HRTSim
task simulator for Real-time tasks and Non-Real-time tasks

## Policy
- Original(Non-DVFS with DRAM, Non-GA)
- **Suggested** GA(DVFS, Hybrid Memory(DRAM and LPM), GA) 

## Input
자세한 내용은 파일 내부의 설명을 참고하세요.
- input_configuration.txt: 메모리, 프로세서, 시뮬레아션 정보 
- input_ga_result.txt: 유전알고리즘의 결과로 생성된 파일
- input_nonrt_tasks.txt: 비실시간 태스크 정보
- input_rt_tasks.txt: 실시간 태스크 정보 

## Run
시뮬레이션 하고자 하는 정보를 위 input 파일에 형식을 맞추어 입력하고, Main.py를 실행.<br>

## Output
총 전력소모량, 프로세서 Utilization, CPU 전력소모량, 메모리 전력소모량, active 시 전력소모량, idle시 전력소모량 등이 콘솔로 출력.

## Demo
...

