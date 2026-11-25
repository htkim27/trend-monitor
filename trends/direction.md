# 리딩 그룹 방향성 레이더 (Robotics & Frontier AI)
기준일: 2026-11-25 (매주 월요일 오전 자동 갱신)

## 그룹 간 공통 흐름
- **프론티어 모델 + 스킬 하네스 수렴**: 하드웨어 제조사(Unitree `unitree_robotskills`)와 학계(`VLAs Execute, Code Recovers`, `Atomic Policy`, `SkillHarness`)가 공통적으로 프론티어 VLM/LLM을 최상위 에이전트 플래너로 두고 원자 스킬·VLA·코드 복구를 결합하는 하네스 패턴으로 수렴 중 (2026-11-23~25).
- **오픈 시뮬레이션·배포 스택 표준화**: 중국 휴머노이드·양팔 진영(Unitree, I2RT YAM, AgiBot, LimX, Booster)이 MuJoCo·Isaac Lab·ONNX·LeRobot 호환 오픈소스 스택을 빠르게 공개 중 (2026-11-24~25).

## 주요 그룹별 현황
### Unitree Robotics (`lab:unitree`)
- **최근 공식 발표**: `unitree_robotskills` 공개(2026-11-23, [GitHub](https://github.com/unitreerobotics/unitree_robotskills)), `unitree_rl_mjlab` 업데이트(2026-11-25, [GitHub](https://github.com/unitreerobotics/unitree_rl_mjlab)).
- **읽히는 방향**: 단순 저수준 SDK 제공을 넘어 GPT-6 Astra 등 외부 프론티어 AI 모델을 자사 로봇에 바로 연결하는 공식 스킬 하네스 레이어를 직접 제공하기 시작함 (2026-11-23).

### NVIDIA Robotics (`lab:nvidia`)
- **최근 공식 발표**: Cosmos 3 Nano 로컬 Diffusers 구동 가이드(2026-11-25, [Blog](https://developer.nvidia.com/blog/how-to-run-nvidia-cosmos-3-on-local-ai-devices-using-hugging-face-diffusers)), Hugging Face × Isaac Lab + Newton Sim2Real 워크플로(2026-11-25, [HF Blog](https://huggingface.co/blog/nvidia/microduck-obstacle-avoidance)).
- **읽히는 방향**: 월드 모델(Cosmos 3)의 온디바이스 경량 실행과 Newton 물리 엔진·Isaac Lab·Hugging Face 생태계 결합을 밀고 있음 (2026-11-25).

### I2RT · YAM (`lab:i2rt`)
- **최근 공식 발표**: `i2rt-robotics/i2rt` 공식 Python SDK 지속 업데이트(2026-11-25, [GitHub](https://github.com/i2rt-robotics/i2rt)).
- **읽히는 방향**: YAM 양팔 플랫폼의 Python 제어·MuJoCo·LeRobot 호환성 유지 (2026-11-25).

### AgiBot · LimX · Booster (`lab:agibot`, `lab:limx`, `lab:booster`)
- **최근 공식 발표**: AgiBot `genie_sim`/`IsaacCapture`(2026-11-24~25), LimX `humanoid-rl-deploy-python`/`tron2-robot-description`(2026-11-25), Booster `booster_robotics_sdk`(2026-11-25).
- **읽히는 방향**: 중국 휴머노이드 기업들이 시뮬레이션(Isaac/MuJoCo/USD), 원격 데이터 수집, ONNX 기반 경량 배포 스택을 오픈소스로 적극 공개 중 (2026-11-25).

### Google DeepMind / OpenAI / Anthropic
- **최근 발표**: Gemini 4 Neon 벤치마크 성능 도약 보도(2026-11-25, 비공식 해설 [Latent Space](https://latent.space/p/ainews-gemini-4-neon-marks-gdm-s-full-return-as-a-frontier-lab)). 지난 30일 로보틱스 전용 공식 방향성 발표는 추가 수집 대기 중.
